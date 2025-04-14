import os
import uuid
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, Response
from pydantic import BaseModel

# 假設下列模組依然存在
from db import ping_postgres
from redis_client import redis_client, ping_redis
from middleware.get_user_from_token import get_user_from_token
from telethon_client import init_sign_in, complete_sign_in, InitSignInStatus
from config import HTTP_PORT, HTTP_LOG_LEVEL, HTTP_HOST

# -----------------------------
# 整合 OpenTelemetry
# -----------------------------
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import  ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Create a Resource that contains your desired service name and other metadata
# resource = Resource.create({
#     "service.name": SERVICE_NAME,
#     "service.namespace": "my-namespace",  # optional
#     "service.version": "1.0.0",           # optional
# })
resource = Resource.create()
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# 設定全域 tracer provider 為我們建立的 provider
trace.set_tracer_provider(provider)

# 後續就可以安全使用 get_tracer_provider() 來取得 provider
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="tempo:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
# -----------------------------
# Logger 設定 (輸出到檔案與 console)
# -----------------------------
from pythonjsonlogger import jsonlogger

SERVICE_NAME = "auth-service"
logger = logging.getLogger("auth_service")
# 設定日誌等級，HTTP_LOG_LEVEL 為字串 (例如 "info"、"debug")
logger.setLevel(HTTP_LOG_LEVEL.upper() if isinstance(HTTP_LOG_LEVEL, str) else logging.INFO)

# 建立 JSON 格式化器
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(message)s %(service)s %(trace_id)s %(span_id)s %(request_id)s %(user_id)s'
)

# 建立 StreamHandler (console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 建立 FileHandler，並確保日誌資料夾存在
log_dir = "/Users/jacky_li/logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# -----------------------------
# 定義一個 helper 函數，自動從 OpenTelemetry 擷取 trace 與 span
# -----------------------------
def get_default_extra(request: Request, user: dict = None) -> dict:
    span = trace.get_current_span()
    span_context = span.get_span_context()
    # 若 span_context 合法則轉換為 16/32 位元 16 進位字串
    trace_id = format(span_context.trace_id, '032x') if span_context.is_valid else ""
    span_id = format(span_context.span_id, '016x') if span_context.is_valid else ""
    return {
        "service": SERVICE_NAME,
        "trace_id": trace_id,
        "span_id": span_id,
        "request_id": getattr(request.state, "request_id", ""),
        "user_id": user.get("id") if user else None
    }


# -----------------------------
# FastAPI 生命週期與中介軟體設定
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting health checks", extra=get_default_extra(Request, None))
    await ping_redis()
    await ping_postgres()

    yield
    await redis_client.close()


# 建立 FastAPI 應用，並注入 lifespan 參數
app = FastAPI(lifespan=lifespan)
# 自動將 FastAPI 整合進 OpenTelemetry
FastAPIInstrumentor.instrument_app(app)


# 中介軟體：為每個 request 加上唯一 request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# -----------------------------
# Request Model 定義
# -----------------------------
class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str


class CodeSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str
    code: str
    phone_code_hash: str


# -----------------------------
# API Endpoint 定義
# -----------------------------
@app.post("/signin/init")
async def init_sign_in_endpoint(req: InitSignInRequest, request: Request, user: dict = Depends(get_user_from_token)):
    logger.info("Received init sign in request", extra=get_default_extra(request, user))
    try:
        result = await init_sign_in(req.api_id, req.api_hash, req.phone, req.password)
    except Exception as e:
        logger.error("Error during init sign in", extra={**get_default_extra(request, user), "message": str(e)})
        raise HTTPException(status_code=400, detail=str(e))

    if result.status == InitSignInStatus.NEED_CODE:
        response = {"status": result.status, "phone_code": result.phone_code}
    elif result.status == InitSignInStatus.SUCCESS:
        response = {"status": result.status, "user": result.user}
    else:
        logger.error("Invalid init sign in status", extra=get_default_extra(request, user))
        raise HTTPException(status_code=400, detail="Invalid status")

    logger.info("Completed init sign in request", extra=get_default_extra(request, user))
    return response


@app.post("/signin/code")
async def sign_in_code_endpoint(req: CodeSignInRequest, request: Request, user: dict = Depends(get_user_from_token)):
    logger.info("Received sign in code request", extra=get_default_extra(request, user))
    try:
        result = await complete_sign_in(api_id=req.api_id,
                                        api_hash=req.api_hash,
                                        phone=req.phone,
                                        password=req.password,
                                        phone_code_hash=req.phone_code_hash,
                                        code=req.code)
    except Exception as e:
        logger.error("Error during sign in code process", extra={**get_default_extra(request, user), "message": str(e)})
        raise HTTPException(status_code=400, detail=str(e))

    logger.info("Completed sign in code request", extra=get_default_extra(request, user))
    return result


@app.post("/list_dialogs")
async def list_dialogs_endpoint(req: CodeSignInRequest, request: Request):
    logger.info("Received list dialogs request", extra=get_default_extra(request, None))
    try:
        result = await complete_sign_in(api_id=req.api_id,
                                        api_hash=req.api_hash,
                                        phone=req.phone,
                                        password=req.password,
                                        phone_code_hash=req.phone_code_hash,
                                        code=req.code)
    except Exception as e:
        logger.error("Error during list dialogs process", extra={**get_default_extra(request, None), "message": str(e)})
        raise HTTPException(status_code=400, detail=str(e))

    logger.info("Completed list dialogs request", extra=get_default_extra(request, None))
    return result


# -----------------------------
# 主程式：啟動 Uvicorn
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host=HTTP_HOST, port=HTTP_PORT, log_level=HTTP_LOG_LEVEL)