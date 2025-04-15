# routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from logger_config import get_logger
from middleware.get_user_from_token import get_user_from_token  # 假設此模組存在
from telethon_client import init_sign_in, complete_sign_in, InitSignInStatus  # 假設此模組存在

router = APIRouter()
logger = get_logger(__name__)


# Request Model 定義
class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str


class CodeSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str
    code: str
    phone_code_hash: str


@router.post("/signin/init")
async def init_sign_in_endpoint(req: InitSignInRequest, user: dict = Depends(get_user_from_token)):
    logger.info("Received init sign in request")
    try:
        result = await init_sign_in(req.api_id, req.api_hash, req.phone, req.password)
    except Exception as e:
        logger.error(f"Error during init sign in: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if result.status == InitSignInStatus.NEED_CODE:
        return {"status": result.status, "phone_code": result.phone_code}
    elif result.status == InitSignInStatus.SUCCESS:
        return {"status": result.status, "user": result.user}
    else:
        logger.error("Invalid init sign in status")
        raise HTTPException(status_code=400, detail="Invalid status")


@router.post("/signin/code")
async def sign_in_code_endpoint(req: CodeSignInRequest, user: dict = Depends(get_user_from_token)):
    logger.info("Received sign in code request")
    try:
        result = await complete_sign_in(
            api_id=req.api_id,
            api_hash=req.api_hash,
            phone=req.phone,
            password=req.password,
            phone_code_hash=req.phone_code_hash,
            code=req.code
        )
    except Exception as e:
        logger.error(f"Error during sign in code process: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    logger.info("Completed sign in code request")
    return result


@router.post("/list_dialogs")
async def list_dialogs_endpoint(req: CodeSignInRequest):
    logger.info("Received list dialogs request")
    try:
        result = await complete_sign_in(
            api_id=req.api_id,
            api_hash=req.api_hash,
            phone=req.phone,
            password=req.password,
            phone_code_hash=req.phone_code_hash,
            code=req.code
        )
    except Exception as e:
        logger.error(f"Error during list dialogs process: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    logger.info("Completed list dialogs request")
    return result