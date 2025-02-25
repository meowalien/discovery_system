package middleware

import (
	"core/gin_context"
	"github.com/gin-gonic/gin"
	"time"
)

func StartTime() gin.HandlerFunc {
	return func(c *gin.Context) {
		gin_context.RequestStartTime.Set(c, time.Now())
		c.Next()
	}
}
