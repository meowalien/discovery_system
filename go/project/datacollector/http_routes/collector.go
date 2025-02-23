package http_routes

import (
	"github.com/gin-gonic/gin"
)

func Collector() func(r gin.IRoutes) {
	return func(r gin.IRoutes) {
		r.GET("/collector", func(c *gin.Context) {
			c.JSON(200, gin.H{})
		})
	}
}
