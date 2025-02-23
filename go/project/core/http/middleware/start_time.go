package middleware

import (
	"core/gin_context"
	"github.com/gin-gonic/gin"
	"time"
)

func StartTime() func(r gin.IRoutes) {
	return func(r gin.IRoutes) {
		r.Use(func(c *gin.Context) {
			gin_context.RequestStartTime.Set(c, time.Now())
			c.Next()
		})
	}
}
