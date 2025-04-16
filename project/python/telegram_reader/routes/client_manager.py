from typing import cast

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from core.message_consumer import MessageConsumer
from core.telegram_client_manager import TelegramClientManager
from logger_config import get_logger
from routes.module import CreateClientRequest, CreateClientResponse, SignInClientRequest, SignInClientResponse, \
    InitSignInStatus, CompleteSignInRequest
from util.util import is_valid_uuid4

router = APIRouter()
_logger = get_logger(__name__)
manager = TelegramClientManager()


@router.post("/clients", description="Create a new Telegram client")
async def create_client(req: CreateClientRequest) -> CreateClientResponse:
    session_id = await manager.create_client(api_id=req.api_id, api_hash=req.api_hash)
    return CreateClientResponse(session_id=session_id)


@router.post("/clients/{session_id}/load", description="Load a Telegram client to manager")
async def load_client(session_id: str):
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    await manager.load_client(session_id=session_id)


@router.post("/clients/{session_id}/sign_in", description="Sign in to Telegram client")
async def sign_in_client(session_id: str, req: SignInClientRequest) -> SignInClientResponse:
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    phone_code_hash = await manager.sign_in(session_id=session_id, phone=req.phone)

    if phone_code_hash:
        return SignInClientResponse(status=InitSignInStatus.NEED_CODE, phone_code_hash=phone_code_hash)
    else:
        return SignInClientResponse(status=InitSignInStatus.SUCCESS)


@router.post("/clients/{session_id}/complete_sign_in", description="Compleat sign in to Telegram client")
async def complete_sign_in_client(session_id: str, req: CompleteSignInRequest):
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    await manager.complete_sign_in(session_id=cast(UUID4, session_id), phone=req.phone, code=req.code,
                                   phone_code_hash=req.phone_code_hash, password=req.password)


@router.get("/clients", description="List all clients")
async def list_client():
    return await manager.get_clients()


@router.get("/clients/{session_id}/dialogs", description="Get all dialogs for a client")
async def get_dialogs(session_id: str):
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    dialogs = await manager.get_dialogs(session_id)
    return [{dialog.id: dialog.title} for dialog in dialogs]


@router.post("/clients/{session_id}/read_message/start", description="Start to read message for a client")
async def start_read_message(session_id: str):
    # session_id should be a valid UUIDv4
    if not is_valid_uuid4(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    message_consumer = MessageConsumer()
    await manager.register_channel_callback(session_id, message_consumer.on_new_event)
