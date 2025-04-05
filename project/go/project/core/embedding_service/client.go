package embedding_service

import (
	"context"
	"core/config"
	"core/graceful_shutdown"
	"fmt"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"proto"
	"sync/atomic"
)

var embeddingServiceClient atomic.Pointer[proto.EmbeddingServiceClient]

func GetClient() proto.EmbeddingServiceClient {
	c := embeddingServiceClient.Load()
	if c == nil {
		logrus.Fatalf("qdrant client is nil")
	}
	return *c
}

func InitEmbeddingServiceClient() {
	conn, err := grpc.NewClient(fmt.Sprintf("%s:%d", config.GetConfig().EmbeddingService.Host, config.GetConfig().EmbeddingService.Port), grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		logrus.Fatalf("Failed to create EmbeddingService client: %v", err)
	}

	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		c := embeddingServiceClient.Load()
		if c == nil {
			return
		}
		e := conn.Close()
		if e != nil {
			logrus.Errorf("EmbeddingService client close fail: %v", e)
		}
		logrus.Infof("EmbeddingService client finalized")
	})

	client := proto.NewEmbeddingServiceClient(conn)
	swaped := embeddingServiceClient.CompareAndSwap(nil, &client)
	if !swaped {
		logrus.Fatalf("EmbeddingService client already initialized")
	}
}
