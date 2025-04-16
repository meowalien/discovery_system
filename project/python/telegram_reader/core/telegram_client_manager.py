import asyncio
import uuid

from telethon import TelegramClient, errors
from typing import Optional, Dict, Callable, Awaitable

from data_source.postgres_client import get_postgres_session
from db_module.telegram_client import SessionModel
from postgres_session import PostgresSession
from telethon.tl.types import Dialog
from telethon.events import NewMessage
from telethon.tl.types import InputPeerChannel

class TelegramClientManager:
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.lock = asyncio.Lock()

    async def load_client(self, session_id:str):
        with get_postgres_session() as session:
            client = session.query(SessionModel).filter_by(session_id=session_id).first()
            if not client:
                raise Exception(f"Session {session_id} not found in database")
        return await self._load_or_create_client(session_id, client.api_id, client.api_hash)

    async def create_client(self, api_id:int, api_hash:str)->str:
        session_id = str(uuid.uuid4())
        await self._load_or_create_client(session_id, api_id, api_hash)
        return session_id

    async def _load_or_create_client(self, session_id:str, api_id:int, api_hash:str):
        async with self.lock:
            if session_id in self.clients:
                return self.clients[session_id]

            session = PostgresSession(
                session_id=session_id,
                api_id= api_id,
                api_hash=api_hash)
            client = TelegramClient(
                session=session,
                api_id= api_id,
                api_hash=api_hash
            )

            await client.connect()
            self.clients[session_id] = client
            return client

    async def get_clients(self) -> Dict[str, bool]:
        async with self.lock:
            return {session_id:await client.is_user_authorized() for session_id,client  in self.clients.items()}

    async def stop_client(self, session_id:str) -> bool:
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                return False
            await client.disconnect()
            del self.clients[session_id]
            return True

    async def shutdown_all(self):
        async with self.lock:
            for client in self.clients.values():
                await client.disconnect()
            self.clients.clear()


    async def get_user_dialogs(self, session_id:str) -> Optional[list[Dialog]]:
        async with self.lock:
            client = self.clients.get(session_id)
            if not client or not await client.is_user_authorized():
                raise ValueError(f"No authorized client found for session {session_id}")

            dialogs = []
            async for dialog in client.iter_dialogs():
                dialogs.append(dialog)
            return dialogs

    async def register_channel_callback(self, session_id:str, channel_id: int, access_hash: int, callback: Callable[[NewMessage.Event], Awaitable[None]]):
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                raise ValueError(f"No client found for session {session_id}")

            entity = InputPeerChannel(channel_id=channel_id, access_hash=access_hash)

            @client.on(NewMessage(chats=entity))
            async def handler(event: NewMessage.Event):
                await callback(event)

    async def sign_in(self, session_id:str, phone: str, password: Optional[str] = None):
        """
        登入 Telegram 帳號
        :param session_id:
        :param phone:
        :param password:
        :return: None if already authorized, else phone_code_hash
        """
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                raise ValueError(f"No client found for session {session_id}")

            if not await client.is_user_authorized():
                # 尚未授權，送出驗證碼請求
                phone_code = await client.send_code_request(phone)
                return phone_code.phone_code_hash
            else:
                # 已授權，直接以密碼登入
                await client.sign_in(phone=phone, password=password)
                return None

    async def complete_sign_in(self, session_id:str, phone: str, code: str, phone_code_hash: str, password: Optional[str] = None):
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                raise ValueError(f"No client found for session {session_id}")

            try:
                # 嘗試使用驗證碼登入
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            except errors.SessionPasswordNeededError:
                if not password:
                    raise ValueError("Password is required for this account.")
                # 若需要額外密碼驗證，則採用密碼方式登入
                await client.sign_in(password=password)
