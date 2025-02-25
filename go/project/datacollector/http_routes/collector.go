package http_routes

import (
	"github.com/gin-gonic/gin"
)

func collector() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(200, gin.H{})
	}
}
