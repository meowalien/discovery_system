from concurrent import futures
import grpc
from proto import embedding_pb2, embedding_pb2_grpc
from service.embedding_service import get_embedding
from config import CONFIG


class EmbeddingServiceServicer(embedding_pb2_grpc.EmbeddingServiceServicer):
    def GetEmbedding(self, request, context):
        # 取得文字 embedding
        embedding = get_embedding(request.text)
        # 將 numpy array 轉換為 list[float]
        embedding_list = [float(x) for x in embedding]
        return embedding_pb2.EmbeddingResponse(embedding=embedding_list)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    embedding_pb2_grpc.add_EmbeddingServiceServicer_to_server(EmbeddingServiceServicer(), server)
    # 從設定檔中讀取 port 值，若找不到則噴錯
    port = CONFIG.get('grpc', {}).get('port')
    if port is None:
        raise ValueError("Port not found in config file.")
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server started on port {port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping server gracefully...")
        server.stop(0)

if __name__ == '__main__':
    serve()