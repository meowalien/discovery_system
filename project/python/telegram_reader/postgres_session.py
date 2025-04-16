import datetime
import time
from typing import cast
from telethon import types, utils
from telethon.tl.types import InputPhoto, InputDocument, PeerUser, PeerChat, PeerChannel
from telethon.crypto import AuthKey
from telethon.sessions import MemorySession
from telethon.sessions.memory import _SentFileType  # type: ignore

from data_source.postgres_client import get_postgres_session
from db_module.telegram_client import SessionModel, UpdateState, Entity, SentFile


class PostgresSession(MemorySession):
    """
    SQLAlchemy 版本的 PostgresSession，
    使用 PostgreSQL 資料庫儲存 Telegram 登入與狀態資訊。
    每次做 DB 存取時都會創建一個新的 SQLAlchemy Session，
    操作成功時 commit，出錯時 rollback。
    """

    def __init__(self, session_id: str, api_id:int, api_hash:str):
        super().__init__()
        self.save_entities = True
        self.session_id = session_id
        self._api_id = api_id
        self._api_hash = api_hash

        with get_postgres_session() as db:
            session_obj = (
                db.query(SessionModel)
                .filter(SessionModel.session_id == self.session_id)
                .first()
            )
            if session_obj:
                self._dc_id = session_obj.dc_id
                self._server_address = session_obj.server_address
                self._port = session_obj.port
                self._takeout_id = session_obj.takeout_id
                self._auth_key = AuthKey(data=session_obj.auth_key) if session_obj.auth_key else None
                self._api_id = session_obj.api_id
                self._api_hash = session_obj.api_hash
            else:
                # 尚未建立此使用者的 session，初始化並寫入 DB
                self._initialize_session()

    def _initialize_session(self):
        # 設定初始預設值
        self._dc_id = 0
        self._server_address = ''
        self._port = 0
        self._takeout_id = None
        self._auth_key = None
        self._update_session_table()

    def clone(self, to_instance=None):
        cloned = super().clone(to_instance)
        cloned.save_entities = self.save_entities
        return cloned

    def set_dc(self, dc_id, server_address, port):
        super().set_dc(dc_id, server_address, port)
        self._update_session_table()
        with get_postgres_session() as db:
            session_obj = (
                db.query(SessionModel)
                .filter(SessionModel.session_id == self.session_id)
                .first()
            )
            if session_obj and session_obj.auth_key:
                self._auth_key = AuthKey(data=session_obj.auth_key)
            else:
                self._auth_key = None

    @MemorySession.auth_key.setter
    def auth_key(self, value):
        self._auth_key = value
        self._update_session_table()

    @MemorySession.takeout_id.setter
    def takeout_id(self, value):
        self._takeout_id = value
        self._update_session_table()

    def _update_session_table(self):
        """
        每次更新資料庫中的 SessionModel 時，開啟新的 Session 作業，
        先刪除舊記錄，再插入最新內容，並 commit。
        """
        with get_postgres_session() as db:
            # 刪除目前 session_id 的所有紀錄
            db.query(SessionModel).filter(SessionModel.session_id == self.session_id).delete()
            auth_key_data = self._auth_key.key if self._auth_key else b''
            session_obj = SessionModel(
                session_id=self.session_id,
                dc_id=self._dc_id,
                server_address=self._server_address,
                port=self._port,
                auth_key=auth_key_data,
                takeout_id=self._takeout_id,
                api_id = self._api_id,
                api_hash=self._api_hash,
            )
            db.add(session_obj)
            

    # ───────── UpdateState 相關操作 ─────────
    def get_update_state(self, entity_id):
        with get_postgres_session() as db:
            state_obj = db.query(UpdateState).filter(UpdateState.id == entity_id).first()
            ret = None
            if state_obj:
                date_obj = datetime.datetime.fromtimestamp(cast(int, state_obj.date), tz=datetime.timezone.utc)
                ret = types.updates.State(
                    cast(int,state_obj.pts), cast(int,state_obj.qts), date_obj, cast(int, state_obj.seq), unread_count=0
                )
            return ret

    def set_update_state(self, entity_id, state):
        with get_postgres_session() as db:
            state_obj = db.query(UpdateState).filter(UpdateState.id == entity_id).first()
            if state_obj:
                state_obj.pts = state.pts
                state_obj.qts = state.qts
                state_obj.date = int(state.date.timestamp())
                state_obj.seq = state.seq
            else:
                state_obj = UpdateState(
                    id=entity_id,
                    pts=state.pts,
                    qts=state.qts,
                    date=int(state.date.timestamp()),
                    seq=state.seq
                )
                db.add(state_obj)
            

    def get_update_states(self):
        with get_postgres_session() as db:
            rows = db.query(UpdateState).all()
            ret = []
            for row in rows:
                state = types.updates.State(
                    pts=cast(int,row.pts),
                    qts=cast(int,row.qts),
                    date=datetime.datetime.fromtimestamp(cast(int,row.date), tz=datetime.timezone.utc),
                    seq=cast(int,row.seq),
                    unread_count=0
                )
                ret.append((row.id, state))
            return ret

    def save(self):
        # 不再使用長期 session，本方法可以不做實作，或根據需求重構。
        pass

    def close(self):
        # 使用 ephemeral session，所以不保留長期連線，這裡可留空。
        pass

    def delete(self):
        with get_postgres_session() as db:
            db.query(SessionModel).filter(SessionModel.session_id == self.session_id).delete()
            
            return True

    @classmethod
    def list_sessions(cls):
        # 根據需求實作查詢所有 session 的連線字串或識別資訊
        return []

    # ───────── Entity 處理 ─────────
    def process_entities(self, tlo):
        if not self.save_entities:
            return
        rows = self._entities_to_rows(tlo)
        if not rows:
            return
        now_val = int(time.time())
        with get_postgres_session() as db:
            for row in rows:
                # 假設 row 格式為 (id, hash, username, phone, name)
                entity_obj = db.query(Entity).filter(Entity.id == row[0]).first()
                if entity_obj:
                    entity_obj.hash = row[1]
                    entity_obj.username = row[2]
                    entity_obj.phone = row[3]
                    entity_obj.name = row[4]
                    entity_obj.date = now_val
                else:
                    entity_obj = Entity(
                        id=row[0],
                        hash=row[1],
                        username=row[2],
                        phone=row[3],
                        name=row[4],
                        date=now_val
                    )
                    db.add(entity_obj)
            

    def get_entity_rows_by_phone(self, phone):
        with get_postgres_session() as db:
            entity_obj = db.query(Entity).filter(Entity.phone == phone).first()
            return (entity_obj.id, entity_obj.hash) if entity_obj else None

    def get_entity_rows_by_username(self, username):
        with get_postgres_session() as db:
            results = db.query(Entity).filter(Entity.username == username).all()
            if not results:
                return None
            if len(results) > 1:
                results.sort(key=lambda r: r.date or 0)
                for t in results[:-1]:
                    t.username = None
                
            ret = (results[-1].id, results[-1].hash)
            return ret

    def get_entity_rows_by_name(self, name):
        with get_postgres_session() as db:
            entity_obj = db.query(Entity).filter(Entity.name == name).first()
            return (entity_obj.id, entity_obj.hash) if entity_obj else None

    def get_entity_rows_by_id(self, the_id, exact=True):
        with get_postgres_session() as db:
            if exact:
                entity_obj = db.query(Entity).filter(Entity.id == the_id).first()
                ret = (entity_obj.id, entity_obj.hash) if entity_obj else None
            else:
                ids = [
                    utils.get_peer_id(PeerUser(the_id)),
                    utils.get_peer_id(PeerChat(the_id)),
                    utils.get_peer_id(PeerChannel(the_id))
                ]
                entity_obj = db.query(Entity).filter(Entity.id.in_(ids)).first()
                ret = (entity_obj.id, entity_obj.hash) if entity_obj else None
            return ret

    # ───────── 檔案處理 ─────────
    def get_file(self, md5_digest, file_size, cls):
        with get_postgres_session() as db:
            sent_file = db.query(SentFile).filter(
                SentFile.md5_digest == md5_digest,
                SentFile.file_size == file_size,
                SentFile.type == _SentFileType.from_type(cls).value
            ).first()
            ret = None
            if sent_file:
                ret = cls(sent_file.id, sent_file.hash)
            return ret

    def cache_file(self, md5_digest, file_size, instance):
        if not isinstance(instance, (InputDocument, InputPhoto)):
            raise TypeError('Cannot cache %s instance' % type(instance))
        with get_postgres_session() as db:
            sent_file = db.query(SentFile).filter(
                SentFile.md5_digest == md5_digest,
                SentFile.file_size == file_size,
                SentFile.type == _SentFileType.from_type(type(instance)).value
            ).first()
            if sent_file:
                sent_file.id = instance.id
                sent_file.hash = instance.access_hash
            else:
                sent_file = SentFile(
                    md5_digest=md5_digest,
                    file_size=file_size,
                    type=_SentFileType.from_type(type(instance)).value,
                    id=instance.id,
                    hash=instance.access_hash
                )
                db.add(sent_file)
            