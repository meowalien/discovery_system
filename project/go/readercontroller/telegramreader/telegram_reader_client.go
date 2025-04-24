package telegramreader

import (
	"context"
	"go-root/proto_impl/telegram_reader"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type MyTelegramReaderServiceClient interface {
	telegram_reader.TelegramReaderServiceClient
	GetName() string
	Close(ctx context.Context) error
}

type myTelegramReaderServiceClient struct {
	telegram_reader.TelegramReaderServiceClient
	grpcConn *grpc.ClientConn
	hostName string
}

func (m *myTelegramReaderServiceClient) Close(ctx context.Context) error {
	return m.grpcConn.Close()
}

func (m *myTelegramReaderServiceClient) GetName() string {
	return m.hostName
}

func NewMyTelegramReader(addr string, hostName string) (MyTelegramReaderServiceClient, error) {
	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}

	return &myTelegramReaderServiceClient{TelegramReaderServiceClient: telegram_reader.NewTelegramReaderServiceClient(conn), grpcConn: conn, hostName: hostName}, nil
}
