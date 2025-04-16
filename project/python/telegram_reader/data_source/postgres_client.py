import asyncio
import atexit
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy import text, create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from config import POSTGRES_URL
from logger_config import get_logger

_logger = get_logger(__name__)

_engine: Engine | None = None

def postgres_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(POSTGRES_URL, echo=False)
    return _engine


_SessionFactory = sessionmaker(
    bind=postgres_engine()
)


@contextmanager
def postgres_session() -> Session:
    with _SessionFactory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


_async_engine: AsyncSession | None = None

def async_postgres_engine() -> AsyncEngine:
    """
    :return: async session
    """
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_engine(
            POSTGRES_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False
        )
    return _async_engine

_AsyncSessionFactory = async_sessionmaker(
    bind=async_postgres_engine(),
    expire_on_commit=False,
    class_=AsyncSession
)

@asynccontextmanager
async def async_postgres_session() -> AsyncSession:
    async with _AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def ping_postgres():
    """
    ping to PostgreSQL database to verify the connection.
    """
    try:
        async with async_postgres_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))

        with postgres_engine().connect() as conn:
            conn.execute(text("SELECT 1"))

        _logger.info("Postgres connection successful")
    except Exception as e:
        _logger.info(f"Postgres connection failed: {e}")

# 若要測試
if __name__ == "__main__":
    asyncio.run(ping_postgres())