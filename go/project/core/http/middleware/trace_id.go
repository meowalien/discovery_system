package middleware

import (
	"core/gin_context"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

func TraceID() gin.HandlerFunc {
	return func(c *gin.Context) {
		traceID := uuid.New().String()
		gin_context.TraceID.Set(c, traceID)
		c.Header("X-Trace-ID", traceID) // let client know the trace id
		c.Next()
	}
}
