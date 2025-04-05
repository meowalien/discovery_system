package middleware

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

const BodySize2MB = 2 << 20 // 2MB
const BodySize0MB = 0       // 0MB

func LimitBodySize(maxBytes int64) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxBytes)
		c.Next()
	}
}
