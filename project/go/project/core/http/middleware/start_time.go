package middleware

import (
	"core/gincontext"
	"github.com/gin-gonic/gin"
	"time"
)

func StartTime() gin.HandlerFunc {
	return func(c *gin.Context) {
		gincontext.RequestStartTime.Set(c, time.Now())
		c.Next()
	}
}
