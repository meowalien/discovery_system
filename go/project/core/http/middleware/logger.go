package middleware

import (
	"core/gincontext"
	"core/log"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
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
