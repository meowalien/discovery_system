# from dataclasses import dataclass
# from telethon import TelegramClient, errors
# from postgres_session import PostgresSession
# from data_source.postgres_client import get_postgres_engine
# from typing import Optional
#
# @dataclass
# class InitSignInResponse:
#     status: str
#     phone_code: Optional[str] = None
#     user: Optional[str] = None
#
#
#
# async def init_sign_in(api_id: int, api_hash: str, phone: str, password: str) -> InitSignInResponse:
#     """
#     Initiates the sign-in process:
#       - Connects to Telegram using the provided credentials.
#       - If not authorized, sends a code request.
#       - Saves session information in Redis and returns a session_id.
#       - If already authorized, signs in directly.
#     """
#     session =PostgresSession(engine=get_postgres_engine(), session_id=phone)
#     client = TelegramClient(session, api_id, api_hash)
#     await client.connect()
#
#     try:
#         if not await client.is_user_authorized():
#             # Request the code and obtain phone_code_hash
#             phone_code = await client.send_code_request(phone)
#             return InitSignInResponse(status=InitSignInStatus.NEED_CODE, phone_code=phone_code.phone_code_hash)
#         else:
#             # Already authorized; sign in with password and return user info
#             await client.sign_in(phone=phone, password=password)
#             me = await client.get_me()
#             return InitSignInResponse(status=InitSignInStatus.SUCCESS, user=f"{me.first_name} {me.last_name}")
#     finally:
#         await client.disconnect()
#
# async def complete_sign_in(api_id: int, api_hash: str, phone: str, password: str, phone_code_hash: Optional[str], code: str) -> dict:
#     """
#     Completes the sign-in process:
#       - Uses the stored session data from Redis.
#       - Signs in using the code (and falls back to password if needed).
#       - Returns user information on successful sign-in.
#     """
#     session = PostgresSession(engine=get_postgres_engine(), session_id=phone)
#     client = TelegramClient(session, api_id, api_hash)
#     await client.connect()
#     try:
#         try:
#             # 嘗試使用提供的 code 進行登入
#             await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
#         except errors.SessionPasswordNeededError:
#             # 如果需要額外密碼，則改用密碼登入
#             await client.sign_in(password=password)
#         me = await client.get_me()
#         return {"status": "success", "user": f"{me.first_name} {me.last_name}"}
#     finally:
#         await client.disconnect()
#
#
# async def list_dialogs(api_id: int, api_hash: str, phone: str) -> list:
#     """
#     Lists all dialogs (conversations) for the authenticated user.
#       - Connects to Telegram using the provided credentials.
#       - Returns a list of dialog names and IDs.
#     """
#     session = PostgresSession(engine=get_postgres_engine(), session_name=phone)
#     client = TelegramClient(session, api_id, api_hash)
#     await client.connect()
#     try:
#         dialogs = []
#         async for dialog in client.iter_dialogs():
#             dialogs.append({"name": dialog.name, "id": dialog.id})
#         return dialogs
#     finally:
#         await client.disconnect()