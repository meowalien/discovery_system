import asyncio
import uuid
from telethon import TelegramClient, errors, events
from typing import Optional, Dict, Callable, Awaitable

from telethon.events.common import EventBuilder

from data_source.postgres_client import postgres_session
from db_module.telegram_client import SessionModel
from exception.exception import EventHandlerAlreadyExistError
from postgres_session import PostgresSession
from telethon.events import NewMessage
from redis_session_manager import RedisSessionManager

class MyTelegramClient(TelegramClient):
    def __init__(self, session: PostgresSession, api_id: int, api_hash: str):
        super().__init__(session, api_id, api_hash)
        self.session = session
        self.api_id = api_id
        self.api_hash = api_hash
        self.event_handler = None

    def add_event_handler(self, callback: Callable, event: Optional[EventBuilder] = None):
        super().add_event_handler(callback, event)
        self.event_handler = (callback, event)

class TelegramClientManager:
    def __init__(self):
        self.redis_manager = None
        self.clients: Dict[str, MyTelegramClient] = {}
        self.lock = asyncio.Lock()


    def set_redis_manager(self, redis_manager: RedisSessionManager):
        self.redis_manager = redis_manager

    async def load_client(self, session_id: str):
        with postgres_session() as session:
            record = session.query(SessionModel).filter_by(session_id=session_id).first()
            if not record:
                raise Exception(f"Session {session_id} not found in database")
            client = await self._load_or_create_client(session_id, record.api_id, record.api_hash)
            return session_id

    async def unload_client(self, session_id: str):
        async with self.lock:
            if session_id not in self.clients:
                raise Exception(f"Session {session_id} not found in memory")
            client = self.clients.pop(session_id)
            await client.disconnect()
            if self.redis_manager is not None:
                await self.redis_manager.remove_session(session_id)

    async def create_client(self, api_id: int, api_hash: str) -> str:
        session_id = str(uuid.uuid4())
        await self._load_or_create_client(session_id, api_id, api_hash)
        return session_id

    async def get_clients(self) -> Dict[str, bool]:
        async with self.lock:
            return {sid: await c.is_user_authorized() for sid, c in self.clients.items()}

    async def stop_client(self, session_id: str) -> bool:
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                return False
            await client.disconnect()
            self.clients.pop(session_id)
            if self.redis_manager is not None:
                await self.redis_manager.remove_session(session_id)
            return True

    async def shutdown_all(self):
        async with self.lock:
            for client in list(self.clients.values()):
                await client.disconnect()
            self.clients.clear()
            if self.redis_manager is not None:
                await self.redis_manager.clear_sessions()

    async def get_dialogs(self, session_id: str) -> Optional[list]:
        async with self.lock:
            client = self.clients.get(session_id)
            if not client or not await client.is_user_authorized():
                raise ValueError(f"No authorized client found for session {session_id}")
            dialogs = []
            async for dialog in client.iter_dialogs():
                dialogs.append(dialog)
            return dialogs

    async def register_channel_callback(self, session_id: str, callback: Callable[[NewMessage.Event], Awaitable[None]]):
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                raise Exception(f"No client found for session {session_id}")
            if client.event_handler is not None:
                raise EventHandlerAlreadyExistError()
            client.add_event_handler(callback, event=events.NewMessage())

    async def sign_in(self, session_id: str, phone: str):
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                raise ValueError(f"No client found for session {session_id}")
            if not await client.is_user_authorized():
                code = await client.send_code_request(phone)
                return code.phone_code_hash
            return None

    async def complete_sign_in(self, session_id: str, phone: str, code: str, phone_code_hash: str, password: Optional[str] = None):
        async with self.lock:
            client = self.clients.get(session_id)
            if not client:
                raise ValueError(f"No client found for session {session_id}")
            try:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            except errors.SessionPasswordNeededError:
                if not password:
                    raise ValueError("Password is required for this account.")
                await client.sign_in(password=password)

    async def _load_or_create_client(self, session_id: str, api_id: int, api_hash: str) -> MyTelegramClient:
        async with self.lock:
            if session_id in self.clients:
                return self.clients[session_id]
            session = PostgresSession(session_id=session_id, api_id=api_id, api_hash=api_hash)
            client = MyTelegramClient(session=session, api_id=api_id, api_hash=api_hash)
            await client.connect()
            self.clients[session_id] = client
            if self.redis_manager is not None:
                await self.redis_manager.add_session(session_id)
            return client

# Helper to instantiate singleton manager
_telegram_client_manager: TelegramClientManager = None

def telegram_client_manager() -> TelegramClientManager:
    global _telegram_client_manager
    if _telegram_client_manager is None:
        _telegram_client_manager = TelegramClientManager()
    return _telegram_client_manager
