package httpcontroller

import (
	"github.com/gin-gonic/gin"
)

func version(serverVersion string) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(200, gin.H{
			"version": serverVersion,
		})
	}
}
