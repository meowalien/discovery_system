# grpc_interceptors.py
import uuid
from types import SimpleNamespace
from grpc import aio
from logger_config import request_context

class RequestIdInterceptor(aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        # 1) 產生全新 request_id
        request_id = str(uuid.uuid4())
        # 2) 用一個簡易 object 存放到 ContextVar（OTelContextFilter 只看 state.request_id）
        ctx_obj = SimpleNamespace(state=SimpleNamespace(request_id=request_id))
        request_context.set(ctx_obj)
        # 3) 繼續後續 handler
        return await continuation(handler_call_details)