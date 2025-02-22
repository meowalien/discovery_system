package http_routes

import (
	"github.com/gin-gonic/gin"
)

func Version(version string) func(r gin.IRoutes) {
	return func(r gin.IRoutes) {
		r.GET("/version", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"version": version,
			})
		})
	}
}
