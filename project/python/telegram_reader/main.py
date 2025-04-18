# main.py
import uvicorn
from config import  HTTP_PORT, HTTP_LOG_LEVEL
from app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT, log_level=HTTP_LOG_LEVEL)