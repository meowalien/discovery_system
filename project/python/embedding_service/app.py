import threading

def start_grpc():
    from server.grpc_server import serve
    serve()

def start_http():
    from server.http_server import serve
    serve()

if __name__ == '__main__':
    grpc_thread = threading.Thread(target=start_grpc, daemon=True)
    grpc_thread.start()

    http_thread = threading.Thread(target=start_http, daemon=True)
    http_thread.start()

    try:
        grpc_thread.join()
        http_thread.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting...")