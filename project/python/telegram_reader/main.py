import asyncio
import signal

from grpc import aio
import telegram_reader_pb2_grpc

from config import HOSTNAME, GRPC_PORT
from core.telegram_client_manager import telegram_client_manager
from data_source.redis_client import redis_client
from logger_config import get_logger
from routes.grpc import AsyncTelegramReaderServiceServicer
from redis_session_manager import RedisSessionManager

_logger = get_logger(__name__)

async def serve():
    manager = telegram_client_manager()
    redis = redis_client()

    # Start Redis session manager
    redis_session_manager = RedisSessionManager(redis, HOSTNAME)
    await redis_session_manager.start(manager)

    manager.set_redis_manager(redis_session_manager)
    # Start gRPC server
    server = aio.server()
    telegram_reader_pb2_grpc.add_TelegramReaderServiceServicer_to_server(
        AsyncTelegramReaderServiceServicer(manager), server
    )
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    await server.start()
    print(f"gRPC server listening on [::]:{GRPC_PORT}")

    # Wait for shutdown signal
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    print("Got stop signal, shutting down gRPC server...")
    await server.stop(5)

    # Clean up Redis key
    await redis_session_manager.cleanup()

if __name__ == "__main__":
    print(f"Pod hostname (via $HOSTNAME): {HOSTNAME}")
    asyncio.run(serve())
