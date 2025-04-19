from google.protobuf import empty_pb2

import grpc
import telegram_reader_pb2
import telegram_reader_pb2_grpc
from core.message_consumer import MessageConsumer
from core.telegram_client_manager import TelegramClientManager
from kafka_client.kafka_producer import producer
from logger.logger import get_logger
from util.util import is_valid_uuid4

_logger = get_logger(__name__)


class AsyncTelegramReaderServiceServicer(
    telegram_reader_pb2_grpc.TelegramReaderServiceServicer
):
    def __init__(self,manager:TelegramClientManager):
        self.manager = manager

    async def CreateClient(
            self, request: telegram_reader_pb2.CreateClientRequest, context
    ) -> telegram_reader_pb2.CreateClientResponse:
        _logger.info(f"CreateClient: api_id={request.api_id}, api_hash={request.api_hash}")
        try:
            session_id = await self.manager.create_client(
                api_id=request.api_id,
                api_hash=request.api_hash,
            )
            return telegram_reader_pb2.CreateClientResponse(session_id=session_id)
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"CreateClient failed: {e}",
            )

    async def LoadClient(
            self, request: telegram_reader_pb2.LoadClientRequest, context
    ) -> empty_pb2.Empty:
        _logger.info(f"LoadClient: session_id={request.session_id}")
        if not is_valid_uuid4(request.session_id):
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid session ID format",
            )
        await self.manager.load_client(session_id=request.session_id)
        return empty_pb2.Empty()

    async def SignInClient(
            self, request: telegram_reader_pb2.SignInClientRequest, context
    ) -> telegram_reader_pb2.SignInClientResponse:
        _logger.info(f"SignInClient: session_id={request.session_id}, phone={request.phone}")
        if not is_valid_uuid4(request.session_id):
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid session ID format",
            )
        phone_code_hash = await self.manager.sign_in(
            session_id=request.session_id,
            phone=request.phone,
        )
        status = (
            telegram_reader_pb2.SignInClientResponse.NEED_CODE
            if phone_code_hash
            else telegram_reader_pb2.SignInClientResponse.SUCCESS
        )
        return telegram_reader_pb2.SignInClientResponse(
            status=status,
            phone_code_hash=phone_code_hash or "",
        )

    async def CompleteSignInClient(
            self, request: telegram_reader_pb2.CompleteSignInRequest, context
    ) -> empty_pb2.Empty:
        _logger.info(
            f"CompleteSignInClient: session_id={request.session_id}, phone={request.phone}"
        )
        if not is_valid_uuid4(request.session_id):
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid session ID format",
            )
        await self.manager.complete_sign_in(
            session_id=request.session_id,
            phone=request.phone,
            code=request.code,
            phone_code_hash=request.phone_code_hash,
            password=request.password,
        )
        return empty_pb2.Empty()

    async def ListClients(
            self, request: empty_pb2.Empty, context
    ) -> telegram_reader_pb2.ListClientsResponse:
        _logger.info("ListClients")
        sessions = await self.manager.get_clients()
        return telegram_reader_pb2.ListClientsResponse(session_ids=sessions)

    async def GetDialogs(
            self, request: telegram_reader_pb2.GetDialogsRequest, context
    ) -> telegram_reader_pb2.GetDialogsResponse:
        _logger.info(f"GetDialogs: session_id={request.session_id}")
        if not is_valid_uuid4(request.session_id):
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid session ID format",
            )
        dialogs = await self.manager.get_dialogs(request.session_id)
        return telegram_reader_pb2.GetDialogsResponse(
            dialogs=[telegram_reader_pb2.Dialog(id=d.id, title=d.title) for d in dialogs]
        )

    async def StartReadMessage(
            self, request: telegram_reader_pb2.StartReadMessageRequest, context
    ) -> empty_pb2.Empty:
        _logger.info(f"StartReadMessage: session_id={request.session_id}")
        if not is_valid_uuid4(request.session_id):
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid session ID format",
            )
        mc = MessageConsumer(producer())
        await self.manager.register_channel_callback(
            request.session_id,
            mc.on_new_event,
        )
        return empty_pb2.Empty()

    async def UnLoadClient(self, request, context):
        _logger.info(f"UnLoadClient: session_id={request.session_id}")
        if not is_valid_uuid4(request.session_id):
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid session ID format",
            )
        await self.manager.unload_client(request.session_id)
        return empty_pb2.Empty()
