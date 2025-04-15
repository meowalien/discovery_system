# main.py
import uvicorn
from config import HTTP_HOST, HTTP_PORT, HTTP_LOG_LEVEL
from app import app

if __name__ == "__main__":
    uvicorn.run(app, host=HTTP_HOST, port=HTTP_PORT, log_level=HTTP_LOG_LEVEL)