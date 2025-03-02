package httproutes

import (
	"context"
	"core/constant"
	"core/embedding_service"
	"core/qdrantclient"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/qdrant/go-client/qdrant"
	"net/http"
	"proto"
)

func collector() gin.HandlerFunc {
	return func(c *gin.Context) {
		embeddingService := embedding_service.GetClient()
		var requestBody struct {
			Text string `json:"text" binding:"required"`
		}
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
			return
		}

		embedding, err := embeddingService.GetEmbedding(c, &proto.EmbeddingRequest{
			Text: requestBody.Text,
		})
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		newUUID := uuid.NewSHA1(constant.DiscoverySystemNameSpaceUUID, []byte(requestBody.Text)).String()

		client := qdrantclient.GetClient()

		// add embedding to discovery_system collection
		operationInfo, err := client.Upsert(context.Background(), &qdrant.UpsertPoints{
			CollectionName: "discovery_system",
			Points: []*qdrant.PointStruct{
				{
					Id:      qdrant.NewIDUUID(newUUID),
					Vectors: qdrant.NewVectors(embedding.Embedding...),
					Payload: qdrant.NewValueMap(map[string]any{"text": requestBody.Text}),
				},
			},
		})
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		fmt.Println(operationInfo.String())

		c.JSON(http.StatusOK, gin.H{"uuid": newUUID, "result": operationInfo.String()})
	}

}
