import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, create_engine
from config import POSTGRES_URL

# 同步 engine：給 legacy code 用
postgres_engine = create_engine(POSTGRES_URL)

# 非同步 engine：給新 async code 用
async_postgres_engine = create_async_engine(
    POSTGRES_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False
)

async def ping_postgres():
    """
    Async ping to PostgreSQL database to verify the connection.
    """
    try:
        async with postgres_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Postgres connection successful")
    except Exception as e:
        print(f"Postgres connection failed: {e}")

# 若要測試
if __name__ == "__main__":
    asyncio.run(ping_postgres())