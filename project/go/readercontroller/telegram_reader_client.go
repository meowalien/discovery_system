package readercontroller

import (
	"go-root/proto_impl/telegram_reader"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type MyTelegramReaderServiceClient interface {
	telegram_reader.TelegramReaderServiceClient
	GetName() string
}

type myTelegramReaderServiceClient struct {
	telegram_reader.TelegramReaderServiceClient
	name string
}

func (m myTelegramReaderServiceClient) GetName() string {
	return m.name
}

func NewMyTelegramReaderServiceClient(addr string, name string) (MyTelegramReaderServiceClient, error) {
	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}

	return &myTelegramReaderServiceClient{TelegramReaderServiceClient: telegram_reader.NewTelegramReaderServiceClient(conn), name: name}, nil
}
