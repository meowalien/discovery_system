package http_routes

import (
	"core/embedding_service"
	"github.com/gin-gonic/gin"
	"proto"
)

func collector() gin.HandlerFunc {
	return func(c *gin.Context) {
		embeddingService := embedding_service.GetClient()
		embedding, err := embeddingService.GetEmbedding(c, &proto.EmbeddingRequest{
			Text: c.Query("text"),
		})
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(200, gin.H{"embedding": embedding.Embedding})
	}

}
