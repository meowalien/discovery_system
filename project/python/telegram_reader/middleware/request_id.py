# middleware/request_id.py
import uuid
from fastapi import Request, Response
from logger_config import request_context

async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    # 將目前 request 存入 contextvars
    request_context.set(request)
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response