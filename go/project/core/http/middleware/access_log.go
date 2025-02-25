package middleware

import (
	"core/gin_context"
	"core/log"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"math"
	"net/http"
	"os"
	"time"
)

func AccessLog(accessLogger log.Logger) func(r gin.IRoutes) {
	hostname, err := os.Hostname()
	if err != nil {
		hostname = "unknow"
	}
	return func(r gin.IRoutes) {
		r.Use(func(c *gin.Context) {
			c.Next()
			path := c.Request.URL.Path
			clientIP := c.ClientIP()
			method := c.Request.Method
			traceID := gin_context.TraceID.Get(c)
			start := gin_context.RequestStartTime.Get(c)
			stop := time.Since(start)
			latency := int(math.Ceil(float64(stop.Nanoseconds()) / 1000000.0))
			statusCode := c.Writer.Status()
			clientUserAgent := c.Request.UserAgent()
			referer := c.Request.Referer()
			dataLength := c.Writer.Size()
			if dataLength < 0 {
				dataLength = 0
			}

			entry := accessLogger.WithFields(logrus.Fields{
				"startTime":  start,
				"traceID":    traceID,
				"hostname":   hostname,
				"statusCode": statusCode,
				"latency":    latency, // time to process
				"clientIP":   clientIP,
				"method":     method,
				"path":       path,
				"referer":    referer,
				"dataLength": dataLength,
				"userAgent":  clientUserAgent,
			})

			if len(c.Errors) > 0 {
				entry.Error(c.Errors.ByType(gin.ErrorTypePrivate).String())
			} else {
				msg := ""
				if statusCode >= http.StatusInternalServerError {
					entry.Error(msg)
				} else if statusCode >= http.StatusBadRequest {
					entry.Warn(msg)
				} else {
					entry.Info(msg)
				}
			}
		})
	}
}
