import json
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from models import InitSignInRequest, CodeSignInRequest, TelethonLoginSessionData
from redis_client import redis_client, ping_redis
from db import ping_postgres
from session import new_session, Session
from telethon_client import init_sign_in, complete_sign_in, InitSignInStatus


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


@app.post("/signin/init")
async def init_sign_in_endpoint(req: InitSignInRequest):
    """
    API endpoint to initiate sign-in.
      - Accepts api_id, api_hash, phone, and password.
      - Returns a session_id if a code is required, or user info if already signed in.
    """
    try:
        result= await init_sign_in(req.api_id, req.api_hash, req.phone, req.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    session = new_session(TelethonLoginSessionData)
    await session.set_data(TelethonLoginSessionData(
        api_id=req.api_id,
        api_hash=req.api_hash,
        phone=req.phone,
        password=req.password,
        phone_code_hash=result.phone_code
    ))
    match result.status:
        case InitSignInStatus.NEED_CODE:
            return {"status":result.status,"session_id": session.session_id}
        case InitSignInStatus.SUCCESS:
            # Already signed in
            return {"status":result.status,"user": result.user}
        case _:
            raise HTTPException(status_code=400, detail="Invalid status")


@app.post("/signin/code")
async def sign_in_code_endpoint(req: CodeSignInRequest):
    """
    API endpoint to complete sign-in using the received code.
      - Retrieves stored session data from Redis using session_id.
      - Completes the sign-in process using the code.
      - Returns user information on success.
    """
    session = Session(session_id=req.session_id, data_cls=TelethonLoginSessionData)
    session_data = await session.get_data()
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        return await complete_sign_in(session_data, req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from config import port, log_level, host
if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run(app, host=host, port=port, log_level=log_level)