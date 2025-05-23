package grpccontroller

import (
	"context"
	"fmt"
	pb "proto"
)

// Collect 方法為 gRPC 的 RPC 實作
func (s *server) Collect(ctx context.Context, req *pb.CollectorRequest) (*pb.CollectorResponse, error) {
	// 範例：直接回傳一個 dummy 的 uuid 與結果訊息
	fmt.Printf("收到文字：%s\n", req.Text)
	// 在此可整合 embedding_service 與 qdrant 操作
	dummyUUID := "dummy-uuid"
	dummyResult := "操作成功"
	return &pb.CollectorResponse{
		Uuid:   dummyUUID,
		Result: dummyResult,
	}, nil
}
