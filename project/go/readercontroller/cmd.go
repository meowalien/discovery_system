package readercontroller

import (
	"context"
	"fmt"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"go-root/config"
	"go-root/lib/data_source"
	"go-root/lib/env"
	"go-root/lib/graceful_shutdown"
	"go-root/lib/grpc"
	"go-root/lib/log"
	"go-root/proto_impl/reader_controller"
	"go-root/readercontroller/dal"
	"time"
)

func Cmd(cmd *cobra.Command, args []string) {
	// Initialize context
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
	defer cancel()

	globalLogger := log.NewLogger()
	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		e := globalLogger.Close()
		if e != nil {
			logrus.Errorf("logger close fail: %v", e)
		}
		logrus.Info("logger finalized")
	})
	redisClient, err := data_source.NewRedisClient(ctx, config.GetConfig().Redis)

	db, err := data_source.NewGormDB(ctx, config.GetConfig().Postgres.DSN())
	if err != nil {
		globalLogger.Fatalf("failed to connect to database: %v", err)
	}
	dataAccessLayer := dal.NewDAL(db, redisClient)

	globalLogger.Infof("Starting gRPC server...")
	manager, err := NewClientManager(ctx, globalLogger, dataAccessLayer)
	if err != nil {
		globalLogger.Fatalf("failed to create client manager: %v", err)
	}
	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		e := manager.Close(ctx)
		if e != nil {
			globalLogger.Errorf("ClientManager close fail: %v", e)
		}
		globalLogger.Info("ClientManager finalized")
	})

	if err != nil {
		globalLogger.Fatalf("failed to sync client: %v", err)
	}
	controller := NewReaderController(dataAccessLayer, manager)
	server := &GRPCServer{Logger: globalLogger, Controller: controller}
	grpcServer := grpc.NewGrpcEngine()
	reader_controller.RegisterReaderControllerServiceServer(grpcServer, server)
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
