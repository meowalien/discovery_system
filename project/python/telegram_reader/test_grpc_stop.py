# grpc_test.py
import grpc

import telegram_reader_pb2 as pb
import telegram_reader_pb2_grpc as pb_grpc
from google.protobuf import empty_pb2


def unload_client(session_id, stub):
    req = pb.UnLoadClientRequest(session_id=session_id)
    # 如果 session_id 不存在會在 server 端拋 INVALID_ARGUMENT 或 INTERNAL
    stub.UnLoadClient(req)
    return True

def main():
    # 1) 建立 channel 與 stub
    channel = grpc.insecure_channel('telegram-reader:50051')
    stub = pb_grpc.TelegramReaderServiceStub(channel)

    # 2) CreateClient
    api_id   = 24529225
    api_hash = '0abc06cc13bab8c228b59bcca4284800'
    session_id = "63f99658-6f35-4eac-b076-8ee2575a2133"
    password = 'kingkingjin'

    unload_client(session_id,stub)


if __name__ == '__main__':
    main()