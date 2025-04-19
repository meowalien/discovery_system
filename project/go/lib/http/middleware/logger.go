package middleware

import (
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"go-root/lib/gincontext"
	"go-root/lib/log"
)

func Logger(logger log.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		traceID := gincontext.TraceID.Get(c)
		requestStartTime := gincontext.RequestStartTime.Get(c)
		realIP := c.ClientIP()

		logger = logger.WithFields(logrus.Fields{
			"ClientIP":  realIP,
			"TraceID":   traceID,
			"Path":      c.Request.URL.Path,
			"Method":    c.Request.Method,
			"StartTime": requestStartTime,
		})

		gincontext.Logger.Set(c, logger)
	}
}
