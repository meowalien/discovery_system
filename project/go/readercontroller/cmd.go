package readercontroller

import (
	"context"
	"fmt"
	"github.com/spf13/cobra"
	"go-root/lib/env"
	"go-root/lib/graceful_shutdown"
	"go-root/lib/grpc"
	"go-root/lib/log"
	"go-root/proto_impl/reader_controller"
	"time"
)

func Cmd(cmd *cobra.Command, args []string) {
	globalLogger := log.NewLogger()
	globalLogger.Infof("Starting gRPC server...")
	grpcServer := grpc.NewGrpcEngine()
	reader_controller.RegisterReaderControllerServiceServer(grpcServer, &ReaderControllerServer{logger: globalLogger})
	grpcAddr := fmt.Sprintf(":%s", env.GetEnv().GRPCPort)

	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		if err := grpcServer.Stop(ctx); err != nil {
			globalLogger.Errorf("failt to stop grpc server: %v", err)
			return
		}
		globalLogger.Infof("grpc server stopped")
	})
	go func() {
		if err := grpcServer.Start(grpcAddr); err != nil {
			globalLogger.Errorf("failt to start grpc server: %v", err)
		}
	}()
	globalLogger.Infof("grpc server started at %s", grpcAddr)

	graceful_shutdown.WaitForShutdown(time.Second * 5)

}
