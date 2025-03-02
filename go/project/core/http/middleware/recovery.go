package middleware

import (
	"core/gincontext"
	"github.com/gin-gonic/gin"
)

func Recovery() gin.HandlerFunc {
	return gin.CustomRecovery(func(c *gin.Context, err interface{}) {
		c.AbortWithStatusJSON(500, gin.H{"error": "Internal Server Error"})
		gincontext.Logger.Get(c).Errorf("panic recovered: %v", err)
	})
}
