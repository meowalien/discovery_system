
from session_model import PostgresSession

import json
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient, errors
import redis.asyncio as redis
import uvicorn
from contextlib import asynccontextmanager




# 建立 Redis 連線 (請確認 Redis 服務正在執行)
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# ping redis_client
async def ping_redis():
    try:
        await redis_client.ping()
        print("Redis connection successful")
    except redis.ConnectionError:
        print("Redis connection failed")

from sqlalchemy import  create_engine
db_url = "postgresql://postgres:postgres@localhost:5432/discovery_system"
postgres_engine = create_engine(db_url)

from sqlalchemy import text

async def ping_postgres():
    try:
        # 使用 SQLAlchemy 的 engine 來 ping 資料庫
        with postgres_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Postgres connection successful")
    except Exception as e:
        print(f"Postgres connection failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_redis()
    await ping_postgres()
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)

# 定義 API 請求的資料模型
class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str

class CodeSignInRequest(BaseModel):
    session_id: str
    code: str

@app.post("/signin/init")
async def init_sign_in(req: InitSignInRequest):
    """
    第一個 API：
    - 傳入 api_id, api_hash, phone, password
    - 建立 TelegramClient 並呼叫 sign_in(password)
    - 將參數存入 Redis，並回傳一個 session_id
    """
    print('req: ',req)
    session = PostgresSession(engine=postgres_engine, session_name=req.phone)
    # 使用 MemorySession (預設為 None 會用 MemorySession)
    client = TelegramClient(session, req.api_id, req.api_hash)
    try:
        await client.connect()

        # 如果尚未授權則進行密碼登入（若已授權則不會重複登入）
        if not await client.is_user_authorized():
            phone_code_hash = await client.send_code_request(req.phone)
            # 產生一個 session_id 並儲存參數至 Redis
            session_id = str(uuid.uuid4())
            session_data = {
                "api_id": req.api_id,
                "api_hash": req.api_hash,
                "phone": req.phone,
                "password": req.password,
                "phone_code_hash": phone_code_hash.phone_code_hash
            }
            await redis_client.set(f"session:{session_id}", json.dumps(session_data))

            return {"status": "need_code", "session_id": session_id}
        else:
            # 如果已經授權，則直接登入
            await client.sign_in(phone=req.phone, password=req.password)
            me = await client.get_me()
            return {"status": "success", "user": f"{me.first_name} {me.last_name}"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await client.disconnect()
@app.post("/signin/code")
async def sign_in_code(req: CodeSignInRequest):
    """
    第二個 API：
    - 傳入 session_id 與 code
    - 從 Redis 取出之前的參數
    - 使用這些參數建立 TelegramClient，並以 code 進行後續登入
    """
    session_key = f"session:{req.session_id}"
    session_data_str = await redis_client.get(session_key)
    if not session_data_str:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = json.loads(session_data_str)
    api_id = session_data.get("api_id")
    api_hash = session_data.get("api_hash")
    phone = session_data.get("phone")
    phone_code_hash = session_data.get("phone_code_hash")
    password = session_data.get("password")
    session = PostgresSession(engine=postgres_engine, session_name=phone)
    print('phone_code_hash: ',phone_code_hash)
    try:
        client = TelegramClient(session, api_id, api_hash)
        await client.connect()
        try:
            # 使用 code 繼續登入
            await client.sign_in(phone=phone, password=password, code=req.code, phone_code_hash=phone_code_hash)
        except errors.SessionPasswordNeededError:
            # 如果需要密碼，則使用密碼登入
            await client.sign_in(password=password)
        # delete Redis 中的 session 資料
        await redis_client.delete(session_key)
        # 取得登入使用者資訊
        me = await client.get_me()
        await client.disconnect()
        return {"status": "success", "user": f"{me.first_name} {me.last_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    # 使用 uvicorn 啟動 HTTP server
    uvicorn.run(app, host="0.0.0.0", port=8000)

