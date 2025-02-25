package middleware

import (
	"core/gin_context"
	"core/log"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func Logger(logger log.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		traceID := gin_context.TraceID.Get(c)
		requestStartTime := gin_context.RequestStartTime.Get(c)
		realIP := c.ClientIP()

		logger = logger.WithFields(logrus.Fields{
			"ClientIP":  realIP,
			"TraceID":   traceID,
			"Path":      c.Request.URL.Path,
			"Method":    c.Request.Method,
			"StartTime": requestStartTime,
		})

		gin_context.Logger.Set(c, logger)
	}
}
