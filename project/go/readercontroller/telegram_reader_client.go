package readercontroller

import (
	"context"
	"go-root/lib/context_value"
	"go-root/lib/graceful_shutdown"
	"go-root/proto_impl/telegram_reader"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func NewClient(ctx context.Context, addr string) (telegram_reader.TelegramReaderServiceClient, error) {
	logger := context_value.Logger.Get(ctx)

	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}
	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		e := conn.Close()
		if e != nil {
			logger.Errorf("TelegramReader client close fail: %v", e)
		}
	})

	return telegram_reader.NewTelegramReaderServiceClient(conn), nil
}
