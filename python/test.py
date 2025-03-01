import time
import unittest
from concurrent import futures
from unittest.mock import patch

import grpc

from proto import embedding_pb2, embedding_pb2_grpc
from service.grpc_server import EmbeddingServiceServicer
# from service.embedding_service import get_embedding

class TestEmbeddingServiceGRPC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the gRPC server in a separate thread
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        embedding_pb2_grpc.add_EmbeddingServiceServicer_to_server(
            EmbeddingServiceServicer(), cls.server
        )
        cls.port = 50051
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()
        # Wait briefly to ensure the server starts
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop(0)
    # 這行裝飾器是使用 unittest.mock.patch 來「mock」（模擬）指定的函數。在這個例子中，它會取代 service.embedding_service 模組中的 get_embedding 函數，使得在測試期間，不論何時呼叫 get_embedding，都會直接回傳固定值 [1.0, 2.0, 3.0]。這樣可以避免執行實際的函數邏輯，讓測試更穩定且能專注於其他部分的驗證。
    @patch('service.embedding_service.get_embedding', return_value=[1.0, 2.0, 3.0])
    def test_get_embedding(self, mock_get_embedding):
        # Create a channel and stub to call the service
        channel = grpc.insecure_channel(f'localhost:{self.port}')
        stub = embedding_pb2_grpc.EmbeddingServiceStub(channel)
        request = embedding_pb2.EmbeddingRequest(text="Hello gRPC")
        response = stub.GetEmbedding(request)

        print(response.embedding)
        # Check that the response embedding matches the mocked value
        # self.assertEqual(response.embedding, [1.0, 2.0, 3.0])
        # Verify that our get_embedding function was called with the correct input
        # mock_get_embedding.assert_called_once_with("Hello gRPC")


if __name__ == '__main__':
    unittest.main()