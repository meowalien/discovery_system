# app/main.py
import json
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from models import InitSignInRequest, CodeSignInRequest
from redis_client import redis_client, ping_redis
from db import ping_postgres
from telethon_client import init_sign_in, complete_sign_in


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
        result = await init_sign_in(req.api_id, req.api_hash, req.phone, req.password, redis_client)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/signin/code")
async def sign_in_code_endpoint(req: CodeSignInRequest):
    """
    API endpoint to complete sign-in using the received code.
      - Retrieves stored session data from Redis using session_id.
      - Completes the sign-in process using the code.
      - Returns user information on success.
    """
    session_key = f"session:{req.session_id}"
    session_data_str = await redis_client.get(session_key)
    if not session_data_str:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = json.loads(session_data_str)

    try:
        result = await complete_sign_in(session_data, req.code, redis_client)
        # Delete the session data from Redis after successful sign-in
        await redis_client.delete(session_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)