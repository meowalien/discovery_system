package readercontroller

import (
	"context"
	"github.com/redis/go-redis/v9"
	"go-root/lib/data_source"
	"go-root/lib/errs"
	"go-root/proto_impl/telegram_reader"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type MyTelegramReaderServiceClient interface {
	telegram_reader.TelegramReaderServiceClient
	GetName() string
	GetSessions(ctx context.Context) ([]string, error)
	Close(ctx context.Context) error
}

type myTelegramReaderServiceClient struct {
	telegram_reader.TelegramReaderServiceClient
	grpcConn    *grpc.ClientConn
	hostName    string
	redisClient *redis.Client
}

func (m *myTelegramReaderServiceClient) Close(ctx context.Context) error {
	return m.grpcConn.Close()
}

func (m *myTelegramReaderServiceClient) GetSessions(ctx context.Context) ([]string, error) {
	sessionsKey := data_source.MakeKey(REDIS_KEY_PREFIX_TELEGRAM_READER_SESSIONS, m.hostName)
	sessions, e := m.redisClient.SMembers(ctx, sessionsKey).Result()
	if e != nil {
		return nil, errs.New(e)
	}
	return sessions, nil
}

func (m *myTelegramReaderServiceClient) GetName() string {
	return m.hostName
}

func NewMyTelegramReaderServiceClient(addr string, hostName string, redisClient *redis.Client) (MyTelegramReaderServiceClient, error) {
	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}

	return &myTelegramReaderServiceClient{TelegramReaderServiceClient: telegram_reader.NewTelegramReaderServiceClient(conn), grpcConn: conn, hostName: hostName, redisClient: redisClient}, nil
}
