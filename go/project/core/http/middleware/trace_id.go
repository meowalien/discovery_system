package middleware

import (
	"core/gin_context"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

func TraceID() func(r gin.IRoutes) {
	return func(r gin.IRoutes) {
		r.Use(func(c *gin.Context) {
			gin_context.TraceID.Set(c, uuid.New().String())
			c.Next()
		})
	}
}
