from sqlalchemy import  Column, Integer, Text, LargeBinary,  BigInteger, Engine
from sqlalchemy.orm import declarative_base, Session
from telethon import types, utils
from telethon.tl.types import InputPhoto, InputDocument, PeerUser, PeerChat, PeerChannel
from telethon.crypto import AuthKey
from telethon.sessions import MemorySession
from telethon.sessions.memory import _SentFileType
import datetime
import time

# 定義 ORM 的 Base 與各個資料表模型
Base = declarative_base()
schema_name = 'telegram_reader'

# 修改 SessionModel，加入 session_id 以區分不同使用者
class SessionModel(Base):
    __table_args__ = {'schema': schema_name}
    __tablename__ = 'sessions'
    session_id = Column(Text, primary_key=True)  # 新增欄位，作為使用者唯一識別
    dc_id = Column(Integer)
    server_address = Column(Text)
    port = Column(Integer)
    auth_key = Column(LargeBinary)
    takeout_id = Column(Integer)

class Entity(Base):
    __table_args__ = {'schema': schema_name}
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    hash = Column(BigInteger, nullable=False)  # 改為 BigInteger
    username = Column(Text)
    phone = Column(BigInteger)  # 改為 BigInteger
    name = Column(Text)
    date = Column(Integer)

class SentFile(Base):
    __table_args__ = {'schema': schema_name}
    __tablename__ = 'sent_files'
    md5_digest = Column(LargeBinary, primary_key=True)
    file_size = Column(Integer, primary_key=True)
    type = Column(Integer, primary_key=True)
    id = Column(Integer)
    hash = Column(Integer)

class UpdateState(Base):
    __table_args__ = {'schema': schema_name}
    __tablename__ = 'update_state'
    id = Column(Integer, primary_key=True)
    pts = Column(Integer)
    qts = Column(Integer)
    date = Column(Integer)
    seq = Column(Integer)

class PostgresSession(MemorySession):
    """
    SQLAlchemy 版本的 PostgresSession，
    使用 PostgreSQL 資料庫儲存 Telegram 登入與狀態資訊，
    請妥善保管資料庫連線資訊以免資料外洩。
    """

    def __init__(self, engine:Engine, session_id: str):
        print(f"Entering __init__ with session_id={session_id}")
        super().__init__()
        self.save_entities = True
        self.session_id = session_id  # 用以區分不同使用者的 session
        self.engine = engine  # 傳入的 SQLAlchemy Engine
        self.db = Session(bind=self.engine)

        # 載入當前使用者的 session 資料（利用 session_id 區分）
        session_obj = self.db.query(SessionModel).filter(SessionModel.session_id == self.session_id).first()
        if session_obj:
            self._dc_id = session_obj.dc_id
            self._server_address = session_obj.server_address
            self._port = session_obj.port
            self._takeout_id = session_obj.takeout_id
            self._auth_key = AuthKey(data=session_obj.auth_key) if session_obj.auth_key else None
        else:
            # 尚未建立此使用者的 session，做初始化
            self._initialize_session()
            self.db.commit()

        print("Exiting __init__")

    def _initialize_session(self):
        # 根據實際需求初始化 dc 及其他欄位（此處可依需要調整預設值）
        self._dc_id = 0
        self._server_address = ''
        self._port = 0
        self._takeout_id = None
        self._auth_key = None
        self._update_session_table()

    def clone(self, to_instance=None):
        print(f"Entering clone with to_instance={to_instance}")
        cloned = super().clone(to_instance)
        cloned.save_entities = self.save_entities
        cloned.connection_dsn = self.connection_dsn
        print("Exiting clone")
        return cloned

    def set_dc(self, dc_id, server_address, port):
        print(f"Entering set_dc with dc_id={dc_id}, server_address={server_address}, port={port}")
        super().set_dc(dc_id, server_address, port)
        self._update_session_table()
        session_obj = self.db.query(SessionModel).filter(SessionModel.session_id == self.session_id).first()
        if session_obj and session_obj.auth_key:
            self._auth_key = AuthKey(data=session_obj.auth_key)
        else:
            self._auth_key = None
        print("Exiting set_dc")

    @MemorySession.auth_key.setter
    def auth_key(self, value):
        print(f"Entering auth_key.setter with value={value}")
        self._auth_key = value
        self._update_session_table()
        print("Exiting auth_key.setter")

    @MemorySession.takeout_id.setter
    def takeout_id(self, value):
        print(f"Entering takeout_id.setter with value={value}")
        self._takeout_id = value
        self._update_session_table()
        print("Exiting takeout_id.setter")

    def _update_session_table(self):
        print("Entering _update_session_table")
        # 先刪除當前 session_id 的記錄，再插入新的資料
        self.db.query(SessionModel).filter(SessionModel.session_id == self.session_id).delete()
        auth_key_data = self._auth_key.key if self._auth_key else b''
        session_obj = SessionModel(
            session_id=self.session_id,
            dc_id=self._dc_id,
            server_address=self._server_address,
            port=self._port,
            auth_key=auth_key_data,
            takeout_id=self._takeout_id
        )
        self.db.add(session_obj)
        self.db.commit()
        print("Exiting _update_session_table")

    def get_update_state(self, entity_id):
        print(f"Entering get_update_state with entity_id={entity_id}")
        state_obj = self.db.query(UpdateState).filter(UpdateState.id == entity_id).first()
        ret = None
        if state_obj:
            date_obj = datetime.datetime.fromtimestamp(state_obj.date, tz=datetime.timezone.utc)
            ret = types.updates.State(state_obj.pts, state_obj.qts, date_obj, state_obj.seq, unread_count=0)
        print("Exiting get_update_state")
        return ret

    def set_update_state(self, entity_id, state):
        print(f"Entering set_update_state with entity_id={entity_id}, state={state}")
        state_obj = self.db.query(UpdateState).filter(UpdateState.id == entity_id).first()
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
            self.db.add(state_obj)
        self.db.commit()
        print("Exiting set_update_state")

    def get_update_states(self):
        print("Entering get_update_states")
        rows = self.db.query(UpdateState).all()
        ret = []
        for row in rows:
            state = types.updates.State(
                pts=row.pts,
                qts=row.qts,
                date=datetime.datetime.fromtimestamp(row.date, tz=datetime.timezone.utc),
                seq=row.seq,
                unread_count=0
            )
            ret.append((row.id, state))
        print("Exiting get_update_states")
        return ret

    def save(self):
        print("Entering save")
        self.db.commit()
        print("Exiting save")

    def close(self):
        print("Entering close")
        self.db.commit()
        self.db.close()
        print("Exiting close")

    def delete(self):
        print("Entering delete")
        self.db.query(SessionModel).delete()
        self.db.commit()
        print("Exiting delete")
        return True

    @classmethod
    def list_sessions(cls):
        print("Entering list_sessions")
        # ret = [cls().connection_dsn]
        print("Exiting list_sessions")
        return []

    # ─── Entity 處理 ─────────────────────────────
    def process_entities(self, tlo):
        print(f"Entering process_entities with tlo={tlo}")
        if not self.save_entities:
            print("Exiting process_entities (save_entities is False)")
            return
        rows = self._entities_to_rows(tlo)
        if not rows:
            print("Exiting process_entities (no rows)")
            return
        now_val = int(time.time())
        for row in rows:
            # 假設 row 為 (id, hash, username, phone, name)
            entity_obj = self.db.query(Entity).filter(Entity.id == row[0]).first()
            if entity_obj:
                entity_obj.hash = row[1]
                entity_obj.username = row[2]
                entity_obj.phone = row[3]
                entity_obj.name = row[4]
                entity_obj.date = now_val
            else:
                entity_obj = Entity(id=row[0], hash=row[1], username=row[2],
                                      phone=row[3], name=row[4], date=now_val)
                self.db.add(entity_obj)
        self.db.commit()
        print("Exiting process_entities")

    def get_entity_rows_by_phone(self, phone):
        print(f"Entering get_entity_rows_by_phone with phone={phone}")
        entity_obj = self.db.query(Entity).filter(Entity.phone == phone).first()
        print("Exiting get_entity_rows_by_phone")
        return (entity_obj.id, entity_obj.hash) if entity_obj else None

    def get_entity_rows_by_username(self, username):
        print(f"Entering get_entity_rows_by_username with username={username}")
        results = self.db.query(Entity).filter(Entity.username == username).all()
        if not results:
            print("Exiting get_entity_rows_by_username (no results)")
            return None
        if len(results) > 1:
            results.sort(key=lambda t: t.date or 0)
            for t in results[:-1]:
                t.username = None
            self.db.commit()
        ret = (results[-1].id, results[-1].hash)
        print("Exiting get_entity_rows_by_username")
        return ret

    def get_entity_rows_by_name(self, name):
        print(f"Entering get_entity_rows_by_name with name={name}")
        entity_obj = self.db.query(Entity).filter(Entity.name == name).first()
        print("Exiting get_entity_rows_by_name")
        return (entity_obj.id, entity_obj.hash) if entity_obj else None

    def get_entity_rows_by_id(self, id, exact=True):
        print(f"Entering get_entity_rows_by_id with id={id}, exact={exact}")
        if exact:
            entity_obj = self.db.query(Entity).filter(Entity.id == id).first()
            ret = (entity_obj.id, entity_obj.hash) if entity_obj else None
        else:
            ids = [
                utils.get_peer_id(PeerUser(id)),
                utils.get_peer_id(PeerChat(id)),
                utils.get_peer_id(PeerChannel(id))
            ]
            entity_obj = self.db.query(Entity).filter(Entity.id.in_(ids)).first()
            ret = (entity_obj.id, entity_obj.hash) if entity_obj else None
        print("Exiting get_entity_rows_by_id")
        return ret

    # ─── 檔案處理 ─────────────────────────────
    def get_file(self, md5_digest, file_size, cls):
        print(f"Entering get_file with md5_digest={md5_digest}, file_size={file_size}, cls={cls}")
        sent_file = self.db.query(SentFile).filter(
            SentFile.md5_digest == md5_digest,
            SentFile.file_size == file_size,
            SentFile.type == _SentFileType.from_type(cls).value
        ).first()
        ret = None
        if sent_file:
            ret = cls(sent_file.id, sent_file.hash)
        print("Exiting get_file")
        return ret

    def cache_file(self, md5_digest, file_size, instance):
        print(f"Entering cache_file with md5_digest={md5_digest}, file_size={file_size}, instance={instance}")
        if not isinstance(instance, (InputDocument, InputPhoto)):
            raise TypeError('Cannot cache %s instance' % type(instance))
        sent_file = self.db.query(SentFile).filter(
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
            self.db.add(sent_file)
        self.db.commit()
        print("Exiting cache_file")