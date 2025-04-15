# routes/auth.py
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from data_source.postgres_client import async_postgres_engine
from db_module.telegram_client import TelegramClient
from logger_config import get_logger
from middleware.get_user_from_token import get_user_from_token  # 假設此模組存在
from telegram_client_manager import TelegramClientManager

from util.util import is_valid_uuid4

router = APIRouter()
logger = get_logger(__name__)
manager = TelegramClientManager()


class CreateClientRequest(BaseModel):
    api_id: int
    api_hash: str

class CreateClientResponse(BaseModel):
    session_id: str

@router.post("/users/{user_id}/clients", description="Create a new Telegram client")
async def create_client(user_id:str, req: CreateClientRequest)->CreateClientResponse:
    session_id = str(uuid.uuid4())
    with Session(async_postgres_engine) as session:
        # 檢查 session_id 是否存在
        existing_client = session.query(TelegramClient).filter_by(session_id=session_id).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="Session ID already exists")

        session.add(TelegramClient(session_id=session_id, user_id=user_id))
        session.commit()

        # Create a new Telegram client
    await manager.create_client(session_id=session_id, api_id=req.api_id, api_hash=req.api_hash)
    return CreateClientResponse(session_id=session_id)


class SignInClientRequest(BaseModel):
    phone: str
    password: str

class SignInClientResponse(BaseModel):
    status: str
    phone_code_hash: Optional[str] = None

class InitSignInStatus:
    NEED_CODE = "need_code"
    SUCCESS = "success"

@router.post("/users/{user_id}/clients/{session_id}/sign_in", description="Sign in to Telegram client")
async def sign_in_client(user_id:str, session_id: str, req: SignInClientRequest) ->SignInClientResponse:
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    phone_code_hash = await manager.sign_in(session_id=session_id, phone=req.phone, password=req.password)

    if phone_code_hash:
        return SignInClientResponse(status=InitSignInStatus.NEED_CODE, phone_code_hash=phone_code_hash)
    else:
        return SignInClientResponse(status=InitSignInStatus.SUCCESS)


class CompleteSignInRequest(BaseModel):
    phone: str
    password: Optional[str] = None
    code: str
    phone_code_hash: str


@router.post("/users/{user_id}/clients/{session_id}/complete_sign_in", description="sign in to Telegram client")
async def complete_sign_in_client(user_id:str, session_id: str, req: CompleteSignInRequest):
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    await manager.complete_sign_in(session_id=session_id, phone=req.phone, code=req.code, phone_code_hash=req.phone_code_hash, password=req.password)

