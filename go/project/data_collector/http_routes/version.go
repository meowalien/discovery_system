package http_routes

import (
	"core"
	"github.com/gin-gonic/gin"
)

func Version(r gin.IRoutes) {
	r.GET("/version", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"version": core.GetEnv().Version,
		})
	})
}
