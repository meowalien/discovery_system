package qdrant

import (
	"context"
	"fmt"
	"log"
	"testing"

	"github.com/qdrant/go-client/qdrant"
)

func TestQdrant(t *testing.T) {
	// Change this based on where your application is running
	//qdrantAddr := "34.81.62.96:6334" // Inside Kubernetes
	// qdrantAddr := "localhost:6334" // If using `kubectl port-forward qdrant 6334:6334 -n qdrant`

	client, err := qdrant.NewClient(&qdrant.Config{
		Host: "34.81.62.96",
		Port: 6334,
	})

	err = client.CreateCollection(context.Background(), &qdrant.CreateCollection{
		CollectionName: "{collection_name}",
		VectorsConfig: qdrant.NewVectorsConfig(&qdrant.VectorParams{
			Size:     4,
			Distance: qdrant.Distance_Cosine,
		}),
	})
	if err != nil {
		log.Fatalf("Failed to create collection: %v", err)
	}

	// Test connection by listing collections
	ctx := context.Background()
	resp, err := client.ListCollections(ctx)
	if err != nil {
		log.Fatalf("Failed to list collections: %v", err)
	}

	fmt.Println("Available collections:", resp)

	err = client.DeleteCollection(context.Background(), "{collection_name}")
	if err != nil {
		log.Fatalf("Failed to delete collection: %v", err)
	}
}
