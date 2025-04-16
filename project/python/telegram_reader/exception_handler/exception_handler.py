from fastapi import FastAPI,Request
from starlette.responses import JSONResponse

from logger_config import get_logger

_logger = get_logger(__name__)


async def generic_exception_handler(request: Request, exc: BaseException):
    _logger.error(f"Exception occurred: {exc}", exc_info=True)
    status_code = 500
    if hasattr(exc, 'status_code'):
        status_code = exc.status_code.value

    message = "Internal Server Error"

    # print all fields of the exception
    if hasattr(exc, 'message') :
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"detail": message}
    )

def append_exception_handler(app:FastAPI):
    app.add_exception_handler(Exception, generic_exception_handler)