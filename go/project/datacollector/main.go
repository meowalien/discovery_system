package main

import (
	"core/config"
	"core/env"
	"core/graceful_shutdown"
	"core/http"
	"core/http/middleware"
	"core/log"
	"data_collector/http_routes"
	"fmt"
	"time"
)

var Version = "unknown"

func main() {
	defer graceful_shutdown.RunFinalizers(5 * time.Second)

	env.InitEnv()
	fmt.Printf("env: %+v\n", env.GetEnv())
	config.InitConfig()
	fmt.Printf("config: %+v\n", config.GetConfig())
	globalLogger := log.NewLogger(env.GetEnv().LogLevel, env.GetEnv().LogFile)
	log.SetGlobalLogger(globalLogger)
	accessLogger := log.NewLogger(env.LogLevelInfo, env.GetEnv().AccessLogFile)

	httpEngine := http.NewHttpEngine(env.GetEnv().Mode)

	httpEngine.Mount(middleware.StartTime())
	httpEngine.Mount(middleware.TraceID())
	httpEngine.Mount(middleware.Logger(globalLogger))
	httpEngine.Mount(middleware.LimitBodySize(middleware.DefaultMaxBodySize))
	httpEngine.Mount(middleware.AccessLog(accessLogger))

	httpEngine.Mount(http_routes.Version(Version))
	httpEngine.Mount(http_routes.Collector())

	addr := fmt.Sprintf(":%s", env.GetEnv().Port)
	go func() {
		if err := httpEngine.Start(addr); err != nil {
			globalLogger.Errorf("failt to start http server: %v", err)
		}
	}()

	globalLogger.Infof("http server started at %s", addr)
	graceful_shutdown.WaitForShutdown()
	globalLogger.Infof("shut down gracefully")
}
