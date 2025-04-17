# grpc_test.py
import grpc

import telegram_reader_pb2 as pb
import telegram_reader_pb2_grpc as pb_grpc
from google.protobuf import empty_pb2

def create_client(api_id, api_hash, stub):
    req = pb.CreateClientRequest(api_id=api_id, api_hash=api_hash)
    resp = stub.CreateClient(req)
    return resp.session_id

def load_client(session_id, stub):
    req = pb.LoadClientRequest(session_id=session_id)
    # 如果 session_id 不存在會在 server 端拋 INVALID_ARGUMENT 或 INTERNAL
    stub.LoadClient(req)
    return True

def sign_in_client(session_id, phone, stub):
    req = pb.SignInClientRequest(session_id=session_id, phone=phone)
    resp = stub.SignInClient(req)
    # 回傳的 status 是 enum：0=SUCCESS, 1=NEED_CODE
    return {
        "status": "need_code" if resp.status == pb.SignInClientResponse.NEED_CODE else "success",
        "phone_code_hash": resp.phone_code_hash
    }

def complete_sign_in_client(session_id, phone, code, phone_code_hash, password, stub):
    req = pb.CompleteSignInRequest(
        session_id=session_id,
        phone=phone,
        code=code,
        phone_code_hash=phone_code_hash,
        password=password or ""
    )
    stub.CompleteSignInClient(req)
    return True

def list_clients(stub):
    resp = stub.ListClients(empty_pb2.Empty())
    return list(resp.session_ids)

def get_dialogs(session_id, stub):
    req = pb.GetDialogsRequest(session_id=session_id)
    resp = stub.GetDialogs(req)
    return [{"id": d.id, "title": d.title} for d in resp.dialogs]

def start_read_message(session_id, stub):
    req = pb.StartReadMessageRequest(session_id=session_id)
    stub.StartReadMessage(req)
    return True

def main():
    # 1) 建立 channel 與 stub
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb_grpc.TelegramReaderServiceStub(channel)

    # 2) CreateClient
    api_id   = 24529225
    api_hash = '0abc06cc13bab8c228b59bcca4284800'
    session_id = "63f99658-6f35-4eac-b076-8ee2575a2133"
    password = 'kingkingjin'
    # print("Created session:", session_id)

    # 3) LoadClient（其實剛建好就不一定要 load，但示範一下）
    load_client(session_id, stub)
    print("Loaded session:", session_id)

    # 4) SignInClient
    phone = '+886968893589'
    sign_in = sign_in_client(session_id, phone, stub)
    print("Sign in response:", sign_in)

    if sign_in["status"] == "need_code":
        phone_code_hash = sign_in["phone_code_hash"]
        code = input("Enter verification code: ")
        complete_sign_in_client(session_id, phone, code, phone_code_hash, password, stub)
        print("Completed sign-in")

    # 5) ListClients
    clients = list_clients(stub)
    print("All sessions:", clients)

    # 6) GetDialogs
    dialogs = get_dialogs(session_id, stub)
    print("Dialogs:", dialogs)

    # 7) StartReadMessage
    start_read_message(session_id, stub)
    print("Started reading messages for", session_id)

if __name__ == '__main__':
    main()