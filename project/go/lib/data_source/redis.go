package data_source

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
	"go-root/lib/config"
	"strings"
	"time"
)

// NewRedisClient initializes and returns a *redis.Client
func NewRedisClient(ctx context.Context, redisConfig config.RedisConfig) (*redis.Client, error) {
	opts := &redis.Options{
		Addr:         fmt.Sprintf("%s:%d", redisConfig.Host, redisConfig.Port), // Redis server address
		Password:     redisConfig.Password,                                     // set if your Redis requires a password
		DB:           redisConfig.DB,                                           // use default DB
		DialTimeout:  5 * time.Second,                                          // connection timeout
		ReadTimeout:  3 * time.Second,                                          // read timeout
		WriteTimeout: 3 * time.Second,                                          // write timeout
		PoolSize:     10,                                                       // number of connections in the pool
		MinIdleConns: 3,                                                        // keep a few idle connections
	}

	client := redis.NewClient(opts)

	// Verify connection with a PING
	if err := client.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	return client, nil
}

const separator = ":"

func MakeKey(keys ...string) string {
	return strings.Join(keys, separator)
}
