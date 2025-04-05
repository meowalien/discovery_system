package main

import (
	"context"
	"fmt"
	"google.golang.org/grpc/credentials/insecure"
	"testing"
	"time"

	"google.golang.org/grpc"
	"proto"
)

func TestGetEmbeddingLive(t *testing.T) {
	// 連線至運行於 localhost:50051 的 gRPC 服務
	conn, err := grpc.NewClient("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("無法連線到 localhost:50051: %v", err)
	}
	defer func(conn *grpc.ClientConn) {
		e := conn.Close()
		if e != nil {
			t.Fatalf("關閉連線失敗: %v", e)
		}
	}(conn)

	client := proto.NewEmbeddingServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*100)
	defer cancel()

	// 呼叫 GetEmbedding 方法
	req := &proto.EmbeddingRequest{Text: "測試文本"}
	resp, err := client.GetEmbedding(ctx, req)
	if err != nil {
		t.Fatalf("呼叫 GetEmbedding 失敗: %v", err)
	}
	fmt.Println("resp.Embedding: ", resp.Embedding)
	// 驗證返回的 embedding 是否非空（根據實際服務返回的結果進行調整）
	if len(resp.Embedding) == 0 {
		t.Errorf("返回的 embedding 為空，預期至少有一個值")
	}
}
