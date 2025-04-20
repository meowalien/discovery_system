package main

import (
	"context"
	"errors"
	"fmt"
	"github.com/redis/go-redis/v9"
	"net"
	"time"
)

func watchSetEvents(ctx context.Context, client *redis.Client, key string) error {
	pubsub := client.PSubscribe(ctx, "__keyspace@0__:"+key)
	// call pubsub.Close() after 3 seconds
	//time.AfterFunc(3*time.Second, func() {
	//	pubsub.Close()
	//	fmt.Println("PubSub closed after 3 seconds")
	//})

	//defer pubsub.Close()

	for {
		msg, err := pubsub.ReceiveMessage(ctx)
		if err != nil {
			// 1) Context 被取消（或逾時）
			if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
				fmt.Println("🔒 上層 Context 已結束，退出監聽")
				return err
			}
			// 2) pubsub/Client 被 Close
			if errors.Is(err, redis.ErrClosed) || errors.Is(err, net.ErrClosed) {
				fmt.Println("🔌 Redis 客戶端或 PubSub 已關閉")
				return nil
			}
			// 3) 可能是網路層的永久性錯誤
			fmt.Printf("❌ 接收訊息發生錯誤：%v，準備重試...\n", err)
			time.Sleep(time.Second) // backoff
			continue
		}

		// 如果沒有錯誤，就是正常收到訊息
		fmt.Printf("收到消息: %s (from channel %s)\n", msg.Payload, msg.Channel)
		switch msg.Payload {
		case "sadd":
			fmt.Printf("有成員被加入到 %s\n", key)
		case "srem":
			fmt.Printf("有成員被從 %s 移除\n", key)
		}
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.TODO(), time.Second)
	defer cancel()
	client := redis.NewClient(&redis.Options{
		Addr: "redis:6379",
	})
	if err := watchSetEvents(ctx, client, "telegram_reader_sessions:localhost"); err != nil {
		panic(err)
	}
}
