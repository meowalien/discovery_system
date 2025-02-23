package main

import (
	"context"
	"core/config"
	"core/env"
	"core/graceful_shutdown"
	"core/http"
	"core/log"
	"data_collector/http_routes"
	"fmt"
	"time"
)

var Version = "unknown"

func main() {
	gracefulShutdownQueue := graceful_shutdown.NewGracefulShutdownQueue()
	defer gracefulShutdownQueue.Run(5 * time.Second)
	env.InitEnv()
	fmt.Printf("env: %+v\n", env.GetEnv())
	config.InitConfig()

	globalLogger := log.NewLogger(env.GetEnv().LogLevel, env.GetEnv().LogFile)
	log.SetGlobalLogger(globalLogger)
	gracefulShutdownQueue.Register(func(ctx context.Context) {
		err := globalLogger.Close()
		if err != nil {
			globalLogger.Errorf("fail to close globalLogger: %v", err)
		} else {
			globalLogger.Infof("globalLogger closed")
		}
	})

	httpEngine := http.NewHttpEngine(env.GetEnv().Mode)
	httpEngine.Mount(http_routes.Version(Version))

	addr := fmt.Sprintf(":%s", env.GetEnv().Port)
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
