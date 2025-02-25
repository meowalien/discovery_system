package middleware

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

const DefaultMaxBodySize = 2 << 20 // 2MB

func LimitBodySize(maxBytes int64) func(r gin.IRoutes) {
	return func(r gin.IRoutes) {
		r.Use(func(c *gin.Context) {
			c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxBytes)
			c.Next()
		})
	}
}
