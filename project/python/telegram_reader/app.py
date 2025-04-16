# app.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from logger_config import get_logger
from telemetry import setup_tracing
from middleware.request_id import add_request_id
# from routes.auth import router as auth_router
from routes.client_manager import router as client_manager_router
from data_source.postgres_client import ping_postgres
from data_source.redis_client import ping_redis, redis_client

_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.info("Starting health checks")
    await ping_redis()
    await ping_postgres()
    yield
    # await async_postgres_engine.dispose()
    # postgres_engine.dispose()
    # await redis_client.close()


def create_app() -> FastAPI:
    # 設定 OpenTelemetry
    setup_tracing()

    app = FastAPI(lifespan=lifespan)
    # 自動整合 OpenTelemetry 至 FastAPI
    FastAPIInstrumentor.instrument_app(app)
    # 註冊中介軟體 (middleware)
    app.middleware("http")(add_request_id)
    # include 掉所有路由
    app.include_router(client_manager_router)
    return app


app = create_app()