# logger_config.py
import os
import logging
import contextvars

import pythonjsonlogger
from pythonjsonlogger import jsonlogger
from fastapi import Request
from opentelemetry import trace
from config import SERVICE_NAME, HTTP_LOG_LEVEL, LOG_FILE_PATH

# 建立全域 context 變數，供 middleware 設定 request 物件
request_context: contextvars.ContextVar[Request|None] = contextvars.ContextVar("request_context", default=None)


class OTelContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        request = request_context.get()
        if request is not None:
            request_id = getattr(request.state, "request_id", "")
        else:
            request_id = ""

        span = trace.get_current_span()
        span_context = span.get_span_context()
        trace_id = format(span_context.trace_id, '032x') if span_context.is_valid else ""
        span_id = format(span_context.span_id, '016x') if span_context.is_valid else ""

        record.service = SERVICE_NAME
        record.trace_id = trace_id
        record.span_id = span_id
        record.request_id = request_id
        record.user_id = ""  # 如有 user 資訊，可在此加上
        return True


def get_logger(name: str = SERVICE_NAME):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(HTTP_LOG_LEVEL.upper() if isinstance(HTTP_LOG_LEVEL, str) else logging.INFO)

    # JSON Formatter for file handler
    json_formatter = pythonjsonlogger.json.JsonFormatter(
        '%(asctime)s %(levelname)s %(message)s %(service)s %(trace_id)s %(span_id)s %(request_id)s %(user_id)s'
    )

    # Human-readable formatter for stderr
    text_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s (trace_id=%(trace_id)s span_id=%(span_id)s req_id=%(request_id)s)'
    )

    # Console Handler to stderr with human-readable output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(text_formatter)
    stream_handler.addFilter(OTelContextFilter())
    logger.addHandler(stream_handler)

    # File Handler with JSON output
    log_file_path = os.path.abspath(LOG_FILE_PATH)
    log_file_dir = log_file_path.rsplit('/', 1)[0]  # Get the directory path
    os.makedirs(log_file_dir, exist_ok=True)
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(OTelContextFilter())
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger