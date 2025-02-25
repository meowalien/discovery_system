package middleware

import (
	"github.com/gin-gonic/gin"
)

func Security() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("X-Frame-Options", "DENY")
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("Content-Security-Policy", "default-src 'self'")
		c.Next()
	}
}
