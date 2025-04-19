package middleware

import (
	"github.com/gin-gonic/gin"
	"go-root/lib/gincontext"
	"time"
)

func StartTime() gin.HandlerFunc {
	return func(c *gin.Context) {
		gincontext.RequestStartTime.Set(c, time.Now())
		c.Next()
	}
}
