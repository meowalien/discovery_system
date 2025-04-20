package readercontroller

import (
	"context"
	"errors"
	"fmt"
	"github.com/redis/go-redis/v9"
	"go-root/config"
	"go-root/lib/errs"
	"go-root/lib/log"
	"net"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

type ClientManager interface {
	FindAvailableClient(ctx context.Context) (MyTelegramReaderServiceClient, error)
	SyncClient(ctx context.Context) error
	FindClientBySessionID(ctx context.Context, sessionID string) (MyTelegramReaderServiceClient, bool, error)
	Close(ctx context.Context) error
}

type clientManager struct {
	redisClient         *redis.Client
	hostNameToClientMap sync.Map
	sessionToClientMap  sync.Map
	logger              log.Logger
}

func (c *clientManager) Close(ctx context.Context) error {
	//TODO implement me
	panic("implement me")
}

func (c *clientManager) addSessionToClient(sessionID string, client MyTelegramReaderServiceClient) {
	c.sessionToClientMap.Store(sessionID, client)
}

func (c *clientManager) getSessionToClient(sessionID string) (MyTelegramReaderServiceClient, bool) {
	client, ok := c.sessionToClientMap.Load(sessionID)
	if !ok {
		return nil, false
	}
	return client.(MyTelegramReaderServiceClient), true
}

func (c *clientManager) deleteHostNameToClient(hostName string) {
	client, ok := c.hostNameToClientMap.LoadAndDelete(hostName)
	if ok {
		cli := client.(MyTelegramReaderServiceClient)
		err := cli.Close(context.Background())
		if err != nil {
			c.logger.Errorf("failed to close client: %v", err)
		}
	}
}

func (c *clientManager) addHostNameToClient(hostName string, client MyTelegramReaderServiceClient) {
	c.hostNameToClientMap.Store(hostName, client)
}

func (c *clientManager) getHostNameToClient(hostName string) (MyTelegramReaderServiceClient, bool) {
	client, ok := c.hostNameToClientMap.Load(hostName)
	if !ok {
		return nil, false
	}
	return client.(MyTelegramReaderServiceClient), true
}

func (c *clientManager) FindAvailableClient(ctx context.Context) (MyTelegramReaderServiceClient, error) {
	//TODO implement me
	panic("implement me")
}

func (c *clientManager) SyncClient(ctx context.Context) error {
	err := c.synchronizeHostNameToClient(ctx)
	if err != nil {
		return errs.New(err)
	}
	panic("implement me")

	return nil

	////read Set from redis on key "telegram_readers"
	//keys, err := c.redisClient.SMembers(ctx, REDIS_KEY_TELEGRAM_READERS).Result()
	//if err != nil {
	//	return errs.New(err)
	//}
	//
	//for _, key := range keys {
	//	keySlipt := strings.Split(key, ":")
	//	if len(keySlipt) != 2 {
	//		return errs.New(fmt.Errorf("invalid key format: %s", key))
	//	}
	//	hostName := keySlipt[1]
	//	headlessURL := config.GetConfig().TelegramReader.HeadlessURL
	//	fqdn := fmt.Sprintf("%s.%s", hostName, headlessURL)
	//
	//	client, e := NewMyTelegramReaderServiceClient(fqdn, hostName, c.redisClient)
	//	if e != nil {
	//		return errs.New(e)
	//	}
	//	c.addHostNameToClient(hostName, client)
	//
	//	sessions, e := client.GetSessions(ctx)
	//	if e != nil {
	//		return errs.New(e)
	//	}
	//	for _, session := range sessions {
	//		c.addSessionToClient(session, client)
	//	}
	//	c.subscribeRedisSetChange(ctx, hostName, client)
	//}

}

func (c *clientManager) FindClientBySessionID(ctx context.Context, sessionID string) (MyTelegramReaderServiceClient, bool, error) {
	//TODO implement me
	panic("implement me")
}

func (c *clientManager) subscribeRedisSetChange(ctx context.Context, sessionKey string, onAddSession func(sllKeys []string), onDeleteSession func(sllKeys []string)) {
	pubsub := c.redisClient.PSubscribe(ctx, "__keyspace@0__:"+sessionKey)
	readSessions := func() []string {
		//	read all from sessionKey set
		sessions, e := c.redisClient.SMembers(context.Background(), sessionKey).Result()
		if e != nil {
			c.logger.Errorf("redis SMembers error: %v", errs.New(e))
		}
		return sessions
	}

	c.appendToCloseCallback(func() {
		err := pubsub.Close()
		if err != nil {
			c.logger.Errorf("redis PubSub close error: %v", errs.New(err))
		}
	})

	go func() {
		for {
			// ReceiveMessage 會自動處理 SUBSCRIBE, RECONNECT…並回傳 msg 或 err
			msg, err := pubsub.ReceiveMessage(context.Background())
			if err != nil {
				// 2) pubsub/Client 被 Close
				if errors.Is(err, redis.ErrClosed) || errors.Is(err, net.ErrClosed) {
					c.logger.Infof("redis PubSub for %s closed", sessionKey)
					return
				}
				c.logger.Errorf("redis PubSub error: %v, retry in 1 second", err)
				time.Sleep(time.Second) // backoff
				continue
			}

			switch msg.Payload {
			case "sadd":
				sessions := readSessions()
				onAddSession(sessions)
			case "srem":
				sessions := readSessions()
				onDeleteSession(sessions)
			}
		}
	}()

}

func (c *clientManager) loadClientByRedisKey(key string) error {
	keySlipt := strings.Split(key, ":")
	if len(keySlipt) != 2 {
		return errs.New(fmt.Errorf("invalid key format: %s", key))
	}
	hostName := keySlipt[1]
	headlessURL := config.GetConfig().TelegramReader.HeadlessURL
	addr := fmt.Sprintf("%s.%s", hostName, headlessURL)

	client, e := NewMyTelegramReaderServiceClient(addr, hostName, c.redisClient)
	if e != nil {
		return errs.New(e)
	}
	c.addHostNameToClient(hostName, client)
	return nil
}

func (c *clientManager) removeClientByRedisKey(key string) error {
	keySlipt := strings.Split(key, ":")
	if len(keySlipt) != 2 {
		return errs.New(fmt.Errorf("invalid key format: %s", key))
	}
	hostName := keySlipt[1]
	c.deleteHostNameToClient(hostName)
	return nil
}

func (c *clientManager) diffKeys(oldMap map[string]struct{}, newKeys []string) (added []string, missed []string, newMap map[string]struct{}) {
	// 建立新的 map，並在同時收集 Added
	newMap = make(map[string]struct{}, len(newKeys))
	for _, k := range newKeys {
		newMap[k] = struct{}{}
		if _, exists := oldMap[k]; !exists {
			added = append(added, k)
		}
	}

	// 收集 Missed（在舊 map 但不在 newKeys）
	for k := range oldMap {
		if _, exists := newMap[k]; !exists {
			missed = append(missed, k)
		}
	}
	return
}

func (c *clientManager) synchronizeHostNameToClient(ctx context.Context) error {
	keys, err := c.redisClient.SMembers(ctx, REDIS_KEY_TELEGRAM_READERS).Result()
	if err != nil {
		return errs.New(err)
	}

	keysInMemory := atomic.Pointer[map[string]struct{}]{}
	m := make(map[string]struct{})

	// initialize hostNameToClientMap
	for _, key := range keys {
		m[key] = struct{}{}
		e := c.loadClientByRedisKey(key)
		if e != nil {
			return errs.New(e)
		}
	}
	keysInMemory.Store(&m)

	updateKeys := func(newKeys []string) {
		added, missed, newMap := c.diffKeys(*keysInMemory.Load(), newKeys)
		for _, key := range added {
			e := c.loadClientByRedisKey(key)
			if e != nil {
				c.logger.Errorf("loadClientByRedisKey error: %v", e.Error())
			}
		}
		for _, key := range missed {
			e := c.removeClientByRedisKey(key)
			if e != nil {
				c.logger.Errorf("loadClientByRedisKey error: %v", e.Error())
			}
		}
		keysInMemory.Store(&newMap)
	}

	c.subscribeRedisSetChange(ctx, REDIS_KEY_TELEGRAM_READERS, updateKeys, updateKeys)
	return nil
}

func (c *clientManager) appendToCloseCallback(f func()) {
	panic("implement me")
}

func NewClientManager(redisClient *redis.Client, logger log.Logger) ClientManager {
	return &clientManager{redisClient: redisClient, logger: logger}
}
