from contextlib import asynccontextmanager
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, Response
from db import ping_postgres
from middleware.get_user_from_token import get_user_from_token
from redis_client import redis_client, ping_redis
from telethon_client import init_sign_in, complete_sign_in, InitSignInStatus
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- health checks ---
    await ping_redis()
    await ping_postgres()

    yield
    await redis_client.close()

# Create the FastAPI app with the lifespan context and add the RequestIdMiddleware
app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str

@app.post("/signin/init")
async def init_sign_in_endpoint(req: InitSignInRequest, user: dict = Depends(get_user_from_token)):
    print("user: ",user)
    try:
        result = await init_sign_in(req.api_id, req.api_hash, req.phone, req.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    match result.status:
        case InitSignInStatus.NEED_CODE:
            return {"status": result.status, "phone_code": result.phone_code}
        case InitSignInStatus.SUCCESS:
            return {"status": result.status, "user": result.user}
        case _:
            raise HTTPException(status_code=400, detail="Invalid status")

class CodeSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str
    code: str
    phone_code_hash: str

@app.post("/signin/code")
async def sign_in_code_endpoint(req: CodeSignInRequest, user: dict = Depends(get_user_from_token)):
    try:
        return await complete_sign_in(api_id=req.api_id,
                                      api_hash=req.api_hash,
                                      phone=req.phone,
                                      password=req.password,
                                      phone_code_hash=req.phone_code_hash,
                                      code=req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/list_dialogs")
async def list_dialogs_endpoint(req: CodeSignInRequest):
    try:
        return await complete_sign_in(api_id=req.api_id,
                                      api_hash=req.api_hash,
                                      phone=req.phone,
                                      password=req.password,
                                      phone_code_hash=req.phone_code_hash,
                                      code=req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from config import HTTP_PORT, HTTP_LOG_LEVEL, HTTP_HOST

if __name__ == "__main__":
    uvicorn.run(app, host=HTTP_HOST, port=HTTP_PORT, log_level=HTTP_LOG_LEVEL)