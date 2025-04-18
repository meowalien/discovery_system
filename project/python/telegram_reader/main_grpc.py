import asyncio

from grpc import aio

import telegram_reader_pb2_grpc
from logger_config import get_logger
from routes.grpc import AsyncTelegramReaderServiceServicer

_logger = get_logger(__name__)


async def serve():
    server = aio.server()
    telegram_reader_pb2_grpc.add_TelegramReaderServiceServicer_to_server(
        AsyncTelegramReaderServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("gRPC server listening on [::]:50051")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
