package main

import (
	"context"
	"core"
	"fmt"
	"github.com/gin-gonic/gin"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	gracefulShutdownQueue := core.NewGracefulShutdownQueue()
	defer gracefulShutdownQueue.Run(5 * time.Second)
	core.InitEnv()
	core.InitConfig()
	gracefulShutdownQueue.Register(func(ctx context.Context) {
		core.FinalizeLoggers()
	})
	globalLogger := core.NewLogger(core.GetEnv().LogLevel, core.GetEnv().LogFile)
	core.SetGlobalLogger(globalLogger)

	version := core.GetConfig().Version
	globalLogger.Infof("version: %s", version)

	httpEngine := core.NewHttpEngine()

	httpEngine.Mount(func(r gin.IRoutes) {
		r.GET("/version", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"version": version,
			})
		})
	})

	addr := fmt.Sprintf(":%s", core.GetEnv().Port)
	if err := httpEngine.Start(addr); err != nil {
		log.Fatalf("failt to start http server: %v", err)
	}

	gracefulShutdownQueue.Register(func(ctx context.Context) {
		if err := httpEngine.Stop(ctx); err != nil {
			globalLogger.Errorf("fail to stop http server: %v", err)
		} else {
			globalLogger.Infof("http server stopped")
		}
	})

	gracefulShutdownQueue.WaitForShutdown()

}
