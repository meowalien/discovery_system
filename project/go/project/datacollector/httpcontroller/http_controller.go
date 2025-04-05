package httpcontroller

import (
	"core/env"
	"core/http"
	"core/http/middleware"
	"core/log"
)

func MountRoutes(httpEngine http.HTTPEngine, serverVersion string, globalLogger log.Logger) {
	accessLogger := log.NewLogger(env.LogLevelInfo, env.GetEnv().AccessLogFile)
	httpEngine.Use(middleware.StartTime())
	httpEngine.Use(middleware.Security())
	httpEngine.Use(middleware.TraceID())
	httpEngine.Use(middleware.Logger(globalLogger))
	httpEngine.Use(middleware.Recovery())
	httpEngine.Use(middleware.AccessLog(accessLogger))

	// list all routes here
	httpEngine.GET("/version", middleware.LimitBodySize(middleware.BodySize0MB), version(serverVersion))
	httpEngine.POST("/collect", collect())
}
