package main

import (
	"context"
	"core"
	"data_collector/http_routes"
	"fmt"
	"time"
)

func main() {
	gracefulShutdownQueue := core.NewGracefulShutdownQueue()
	defer gracefulShutdownQueue.Run(5 * time.Second)
	core.InitEnv()
	core.InitConfig()

	globalLogger := core.NewLogger(core.GetEnv().LogLevel, core.GetEnv().LogFile)
	core.SetGlobalLogger(globalLogger)
	gracefulShutdownQueue.Register(func(ctx context.Context) {
		err := globalLogger.Close()
		if err != nil {
			globalLogger.Errorf("fail to close globalLogger: %v", err)
		} else {
			globalLogger.Infof("globalLogger closed")
		}
	})

	httpEngine := core.NewHttpEngine(core.GetEnv().Mode)
	httpEngine.Mount(http_routes.Version)

	addr := fmt.Sprintf(":%s", core.GetEnv().Port)
	if err := httpEngine.Start(addr); err != nil {
		globalLogger.Errorf("failt to start http server: %v", err)
	}

	gracefulShutdownQueue.Register(func(ctx context.Context) {
		if err := httpEngine.Stop(ctx); err != nil {
			globalLogger.Errorf("fail to stop http server: %v", err)
		} else {
			globalLogger.Infof("http server stopped")
		}
	})

	gracefulShutdownQueue.WaitForShutdown()
	globalLogger.Infof("shut down gracefully")
}
