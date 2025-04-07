from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from db import ping_postgres
from redis_client import redis_client, ping_redis
from telethon_client import init_sign_in, complete_sign_in, InitSignInStatus
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan function to perform startup and shutdown tasks.
    It pings Redis and PostgreSQL to ensure connections are available.
    """
    await ping_redis()
    ping_postgres()  # Synchronous ping; consider wrapping if needed.
    yield
    await redis_client.close()


# Create the FastAPI app with the lifespan context
app = FastAPI(lifespan=lifespan)

# @app.middleware("http")
# async def jwt_auth_middleware(request: Request, call_next):
#
#     auth: str | None = request.headers.get("Authorization")
#     if not auth or not auth.lower().startswith("bearer "):
#         return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})
#
#     token = auth.split(" ", 1)[1]
#
#
#     return await call_next(request)


class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str


@app.post("/signin/init")
async def init_sign_in_endpoint(req: InitSignInRequest):
    """
    API endpoint to initiate sign-in.
      - Accepts api_id, api_hash, phone, and password.
      - Returns phone_code if a code is required, or user info if already signed in.
    """
    try:
        result = await init_sign_in(req.api_id, req.api_hash, req.phone, req.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    match result.status:
        case InitSignInStatus.NEED_CODE:
            # 直接回傳 phone_code 給前端，不儲存 session
            return {"status": result.status, "phone_code": result.phone_code}
        case InitSignInStatus.SUCCESS:
            # Already signed in
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
async def sign_in_code_endpoint(req: CodeSignInRequest):
    """
    API endpoint to complete sign-in using the received code.
      - Accepts all necessary parameters from the frontend.
      - Completes the sign-in process using the provided data and code.
      - Returns user information on success.
    """
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
async def sign_in_code_endpoint(req: CodeSignInRequest):
    """
    API endpoint to complete sign-in using the received code.
      - Accepts all necessary parameters from the frontend.
      - Completes the sign-in process using the provided data and code.
      - Returns user information on success.
    """
    try:
        return await complete_sign_in(api_id=req.api_id,
                                      api_hash=req.api_hash,
                                      phone=req.phone,
                                      password=req.password,
                                      phone_code_hash=req.phone_code_hash,
                                      code=req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from config import port, log_level, host

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run(app, host=host, port=port, log_level=log_level)
