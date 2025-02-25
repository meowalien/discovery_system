package qdrant

import (
	"context"
	"core/config"
	"core/graceful_shutdown"
	"github.com/qdrant/go-client/qdrant"
	"github.com/sirupsen/logrus"
	"sync/atomic"
)

var qdrantClient atomic.Pointer[qdrant.Client]

func GetClient() *qdrant.Client {
	c := qdrantClient.Load()
	if c == nil {
		logrus.Fatalf("qdrant client is nil")
	}
	return c
}

func InitQdrant() {
	client, err := qdrant.NewClient(&qdrant.Config{
		Host:   config.GetConfig().Qdrant.Host,
		Port:   config.GetConfig().Qdrant.Port,
		APIKey: config.GetConfig().Qdrant.APIKey,
	})
	if err != nil {
		logrus.Fatalf("Failed to create qdrant client: %v", err)
	}
	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		c := qdrantClient.Load()
		if c == nil {
			return
		}
		e := c.Close()
		if e != nil {
			logrus.Errorf("qdrant client close fail: %v", e)
		}
		logrus.Infof("qdrant client finalized")
	})

	swaped := qdrantClient.CompareAndSwap(nil, client)
	if !swaped {
		logrus.Fatalf("Qdrant client already initialized")
	}
}
