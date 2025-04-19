package readercontroller

import (
	"context"
	"github.com/redis/go-redis/v9"
	"go-root/lib/errs"
	"go-root/proto_impl/telegram_reader"
	"strings"
)

type ClientManager interface {
	FindAvailableClient(ctx context.Context) (MyTelegramReaderServiceClient, error)
	SyncClient(ctx context.Context) error
	FindClientBySessionID(ctx context.Context, sessionID string) (MyTelegramReaderServiceClient, bool, error)
}

type clientManager struct {
	redisClient *redis.Client
}

func (c *clientManager) FindAvailableClient(ctx context.Context) (MyTelegramReaderServiceClient, error) {
	//TODO implement me
	panic("implement me")
}

func (c *clientManager) SyncClient(ctx context.Context) error {
	//read Set from redis on key "telegram_readers"
	keys, err := c.redisClient.SMembers(ctx, REDIS_KEY_TELEGRAM_READERS).Result()
	if err != nil {
		return errs.New(err)
	}
	//for each key, create a new client and add to the list
	clients := make([]MyTelegramReaderServiceClient, 0)
	for _, key := range keys {
		hostName := strings.Split(key, ":")[1]

		client, err := NewMyTelegramReaderServiceClient(key, key)
		if err != nil {
			return errs.New(err)
		}
		clients = append(clients, client)
	}
}

func (c *clientManager) FindClientBySessionID(ctx context.Context, sessionID string) (MyTelegramReaderServiceClient, bool, error) {
	//TODO implement me
	panic("implement me")
}

func NewClientManager(redisClient *redis.Client) ClientManager {
	return &clientManager{redisClient: redisClient}
}
