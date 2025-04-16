import uuid
from typing import Optional, cast
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, UUID4
from data_source.postgres_client import  get_postgres_session
from db_module.telegram_client import SessionModel
from logger_config import get_logger
from telegram_client_manager import TelegramClientManager

from util.util import is_valid_uuid4

router = APIRouter()
logger = get_logger(__name__)
manager = TelegramClientManager()


class CreateClientRequest(BaseModel):
    api_id: int
    api_hash: str

class CreateClientResponse(BaseModel):
    session_id: UUID4

@router.post("/clients", description="Create a new Telegram client")
async def create_client(req: CreateClientRequest)->CreateClientResponse:
    session_id = str(uuid.uuid4())

    await manager.create_client(session_id=session_id, api_id=req.api_id, api_hash=req.api_hash)

    return CreateClientResponse(session_id=session_id)


@router.post("/clients/{session_id}/load", description="Load a Telegram client to manager")
async def sign_in_client(session_id: str) :
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if the session_id exists in the database
    with get_postgres_session() as session:
        client = session.query(SessionModel).filter_by(session_id=session_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Session ID not found")


    await manager.create_client(session_id=session_id, api_id=client.api_id, api_hash=client.api_hash)


class SignInClientRequest(BaseModel):
    phone: str
    password: str

class SignInClientResponse(BaseModel):
    status: str
    phone_code_hash: Optional[str] = None

class InitSignInStatus:
    NEED_CODE = "need_code"
    SUCCESS = "success"

@router.post("/clients/{session_id}/sign_in", description="Sign in to Telegram client")
async def sign_in_client(session_id: str, req: SignInClientRequest) ->SignInClientResponse:
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


@router.post("/clients/{session_id}/complete_sign_in", description="Compleat sign in to Telegram client")
async def complete_sign_in_client(session_id: str, req: CompleteSignInRequest):
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    await manager.complete_sign_in(session_id=cast(UUID4,session_id), phone=req.phone, code=req.code, phone_code_hash=req.phone_code_hash, password=req.password)


@router.get("/clients", description="List all clients")
async def list_client():
    return await manager.get_clients()