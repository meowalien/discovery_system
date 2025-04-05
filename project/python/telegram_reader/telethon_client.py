# app/telethon_client.py
import uuid
import json
from telethon import TelegramClient, errors
from session_model import PostgresSession  # Your custom Telethon session model
from db import postgres_engine

async def init_sign_in(api_id: int, api_hash: str, phone: str, password: str, redis_client) -> dict:
    """
    Initiates the sign-in process:
      - Connects to Telegram using the provided credentials.
      - If not authorized, sends a code request.
      - Saves session information in Redis and returns a session_id.
      - If already authorized, signs in directly.
    """
    session = PostgresSession(engine=postgres_engine, session_name=phone)
    client = TelegramClient(session, api_id, api_hash)
    await client.connect()

    try:
        if not await client.is_user_authorized():
            # Request the code and obtain phone_code_hash
            phone_code = await client.send_code_request(phone)
            session_id = str(uuid.uuid4())
            session_data = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone": phone,
                "password": password,
                # Save phone_code_hash only if available
                "phone_code_hash": phone_code.phone_code_hash if phone_code else None,
            }
            await redis_client.set(f"session:{session_id}", json.dumps(session_data))
            return {"status": "need_code", "session_id": session_id}
        else:
            # Already authorized; sign in with password and return user info
            await client.sign_in(phone=phone, password=password)
            me = await client.get_me()
            return {"status": "success", "user": f"{me.first_name} {me.last_name}"}
    finally:
        await client.disconnect()

async def complete_sign_in(session_data: dict, code: str, redis_client) -> dict:
    """
    Completes the sign-in process:
      - Uses the stored session data from Redis.
      - Signs in using the code (and falls back to password if needed).
      - Returns user information on successful sign-in.
    """
    api_id = session_data.get("api_id")
    api_hash = session_data.get("api_hash")
    phone = session_data.get("phone")
    password = session_data.get("password")
    phone_code_hash = session_data.get("phone_code_hash")

    session = PostgresSession(engine=postgres_engine, session_name=phone)
    client = TelegramClient(session, api_id, api_hash)
    await client.connect()
    try:
        try:
            # Attempt to sign in using the provided code
            await client.sign_in(phone=phone, password=password, code=code, phone_code_hash=phone_code_hash)
        except errors.SessionPasswordNeededError:
            # If a password is additionally required, sign in with the password
            await client.sign_in(password=password)
        me = await client.get_me()
        return {"status": "success", "user": f"{me.first_name} {me.last_name}"}
    finally:
        await client.disconnect()