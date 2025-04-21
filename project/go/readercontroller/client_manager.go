package readercontroller

import (
	"container/heap"
	"context"
	"errors"
	"fmt"
	"github.com/redis/go-redis/v9"
	"go-root/config"
	"go-root/lib/errs"
	"go-root/lib/log"
	"net"
	"sync"
	"sync/atomic"
	"time"
)

type ClientManager interface {
	FindAvailableClient(ctx context.Context) (MyTelegramReaderServiceClient, error)
	FindClientBySessionID(ctx context.Context, sessionID string) (MyTelegramReaderServiceClient, bool, error)
	Close(ctx context.Context) error
}

type clientManager struct {
	redisClient                       redis.UniversalClient
	dal                               DAL
	logger                            log.Logger
	sessionIDToClientMap              sync.Map // *myTelegramReaderServiceClientWithReferenceCount
	hostNameToSessionID               sync.Map //map[string]map[string]struct{}
	serviceClientWithSessionCountHeap telegramReaderServiceClientHeap
}

func (c *clientManager) Close(ctx context.Context) error {
	//TODO implement me
	panic("implement me")
}

func (c *clientManager) FindAvailableClient(ctx context.Context) (MyTelegramReaderServiceClient, error) {
	//TODO implement me
	panic("implement me")
}

// this should be called only once when the object is created
func (c *clientManager) syncReaders(ctx context.Context) error {
	onNew, onDelete, onError, closeFunc := c.dal.SubscribeTelegramReaderChange(ctx)
	c.onCloseCallback(func() {
		err := closeFunc()
		if err != nil {
			c.logger.Errorf("error when close SubscribeTelegramReader: %v", errs.New(err))
		}
	})

	go func() {
		for {
			select {
			case newClientHostNames, ok := <-onNew:
				if !ok {
					return
				}
				timeoutCtx, cancel := context.WithTimeout(ctx, time.Second*5)
				for _, hostName := range newClientHostNames {
					e := c.loadClientByHostName(timeoutCtx, hostName)
					if e != nil {
						c.logger.Errorf("loadClientByHostName error: %v", errs.New(e))
					}
				}
				cancel()

			case deletedClientHostNames, ok := <-onDelete:
				if !ok {
					return
				}
				timeoutCtx, cancel := context.WithTimeout(ctx, time.Second*5)
				for _, hostName := range deletedClientHostNames {
					e := c.removeClientByHostName(timeoutCtx, hostName)
					if e != nil {
						c.logger.Errorf("loadClientByHostName error: %v", errs.New(e))
					}
				}
				cancel()
			case err, ok := <-onError:
				if !ok {
					return
				}
				c.logger.Errorf("error when reading SubscribeTelegramReaderChange: %v", errs.New(err))
			}
		}
	}()

	return nil
}

func (c *clientManager) FindClientBySessionID(ctx context.Context, sessionID string) (MyTelegramReaderServiceClient, bool, error) {
	//TODO implement me
	panic("implement me")
}

//func (c *clientManager) subscribeRedisSetChange(ctx context.Context, sessionKey string, onAddSession func(sllKeys []string), onDeleteSession func(sllKeys []string)) (closeFunc func() error) {
//	pubsub := c.redisClient.PSubscribe(ctx, "__keyspace@0__:"+sessionKey)
//	readSessions := func() []string {
//		//	read all from sessionKey set
//		sessions, e := c.redisClient.SMembers(context.Background(), sessionKey).Result()
//		if e != nil {
//			c.logger.Errorf("redis SMembers error: %v", errs.New(e))
//		}
//		return sessions
//	}
//	closeFunc = pubsub.Close
//
//	go func() {
//		for {
//			// ReceiveMessage 會自動處理 SUBSCRIBE, RECONNECT…並回傳 msg 或 err
//			msg, err := pubsub.ReceiveMessage(context.Background())
//			if err != nil {
//				// 2) pubsub/Client 被 Close
//				if errors.Is(err, redis.ErrClosed) || errors.Is(err, net.ErrClosed) {
//					c.logger.Infof("redis PubSub for %s closed", sessionKey)
//					return
//				}
//				c.logger.Errorf("redis PubSub error: %v, retry in 1 second", err)
//				time.Sleep(time.Second) // backoff
//				continue
//			}
//
//			switch msg.Payload {
//			case "sadd":
//				sessions := readSessions()
//				onAddSession(sessions)
//			case "srem":
//				sessions := readSessions()
//				onDeleteSession(sessions)
//			}
//		}
//	}()
//	return closeFunc
//}

//func (c *clientManager) redisKeyToHostName(key string) (string, error) {
//	keySlipt := strings.Split(key, ":")
//	if len(keySlipt) != 2 {
//		return "", errs.New(fmt.Errorf("invalid key format: %s", key))
//	}
//	hostName := keySlipt[1]
//	return hostName, nil
//}

//func (c *clientManager) loadClientByRedisKey(ctx context.Context, key string) error {
//	hostName, err := c.redisKeyToHostName(key)
//	if err != nil {
//		return errs.New(err)
//	}
//	headlessURL := config.GetConfig().TelegramReader.HeadlessURL
//	addr := fmt.Sprintf("%s.%s", hostName, headlessURL)
//
//	client, e := NewMyTelegramReaderServiceClient(addr, hostName, c.redisClient)
//	if e != nil {
//		return errs.New(e)
//	}
//
//	// ======
//
//	sessionsKey := data_source.MakeKey(REDIS_KEY_PREFIX_TELEGRAM_READER_SESSIONS, hostName)
//
//	sessions, err := c.redisClient.SMembers(ctx, sessionsKey).Result()
//	if err != nil {
//		return errs.New(err)
//	}
//
//	sessionsInMemory := atomic.Pointer[map[string]struct{}]{}
//	m := make(map[string]struct{})
//	// initialize hostNameToClientMap
//	for _, session := range sessions {
//		m[session] = struct{}{}
//		c.addSessionToClient(session, client)
//	}
//	sessionsInMemory.Store(&m)
//
//	updateSessions := func(newSessions []string) {
//		added, missed, newMap := c.diffKeys(*sessionsInMemory.Load(), newSessions)
//		for _, session := range added {
//			c.addSessionToClient(session, client)
//		}
//		for _, session := range missed {
//			c.deleteSessionToClient(session)
//		}
//		sessionsInMemory.Store(&newMap)
//	}
//
//	closeFunc := c.subscribeRedisSetChange(ctx, sessionsKey, updateSessions, updateSessions)
//
//	// close when the client is closed
//	client.addOnClose(func(ctx context.Context) error {
//		return closeFunc()
//	})
//
//	c.addHostNameToClient(hostName, client)
//	return nil
//}

//
//func (c *clientManager) removeClientByRedisKey(ctx context.Context, key string) error {
//	hostName, err := c.redisKeyToHostName(key)
//	if err != nil {
//		return errs.New(err)
//	}
//	c.deleteHostNameToClient(hostName)
//	return nil
//}

//func (c *clientManager) diffKeys(oldMap map[string]struct{}, newKeys []string) (added []string, missed []string, newMap map[string]struct{}) {
//	// 建立新的 map，並在同時收集 Added
//	newMap = make(map[string]struct{}, len(newKeys))
//	for _, k := range newKeys {
//		newMap[k] = struct{}{}
//		if _, exists := oldMap[k]; !exists {
//			added = append(added, k)
//		}
//	}
//
//	// 收集 Missed（在舊 map 但不在 newKeys）
//	for k := range oldMap {
//		if _, exists := newMap[k]; !exists {
//			missed = append(missed, k)
//		}
//	}
//	return
//}

//func (c *clientManager) synchronizeHostNameToClient(ctx context.Context) error {
//	keysInMemory := atomic.Pointer[map[string]struct{}]{}
//	m := make(map[string]struct{})
//	keysInMemory.Store(&m)
//
//	// make sure either updating or initializing clients
//	lock := sync.Mutex{}
//
//	updateKeys := func(newKeys []string) {
//		lock.Lock()
//		defer lock.Unlock()
//		ctxTimeoot, cancel := context.WithTimeout(ctx, time.Second*5)
//		defer cancel()
//		added, missed, newMap := c.diffKeys(*keysInMemory.Load(), newKeys)
//		for _, key := range added {
//			e := c.loadClientByRedisKey(ctxTimeoot, key)
//			if e != nil {
//				c.logger.Errorf("loadClientByRedisKey error: %v", e.Error())
//			}
//		}
//		for _, key := range missed {
//			e := c.removeClientByRedisKey(ctxTimeoot, key)
//			if e != nil {
//				c.logger.Errorf("loadClientByRedisKey error: %v", e.Error())
//			}
//		}
//		keysInMemory.Store(&newMap)
//	}
//
//	closeFunc := c.subscribeRedisSetChange(ctx, REDIS_KEY_TELEGRAM_READERS, updateKeys, updateKeys)
//	// close when clientManager close
//	c.onCloseCallback(func() {
//		e := closeFunc()
//		if e != nil {
//			c.logger.Errorf("redis PubSub close error: %v", errs.New(e))
//		}
//	})
//
//	keys, err := c.redisClient.SMembers(ctx, REDIS_KEY_TELEGRAM_READERS).Result()
//	if err != nil {
//		return errs.New(err)
//	}
//
//	initializeClients := func(ctx context.Context, keys []string) error {
//		lock.Lock()
//		defer lock.Unlock()
//		newM := make(map[string]struct{})
//		for _, key := range keys {
//			newM[key] = struct{}{}
//			e := c.loadClientByRedisKey(ctx, key)
//			if e != nil {
//				return errs.New(e)
//			}
//		}
//		keysInMemory.Store(&newM)
//		return nil
//	}
//
//	err = initializeClients(ctx, keys)
//	if err != nil {
//		return errs.New(err)
//	}
//
//	return nil
//}

func (c *clientManager) onCloseCallback(f func()) {
	panic("implement me")
}

func (c *clientManager) loadClientByHostName(ctx context.Context, hostName string) error {
	headlessURL := config.GetConfig().TelegramReader.HeadlessURL
	addr := fmt.Sprintf("%s.%s", hostName, headlessURL)

	client, err := NewMyTelegramReaderServiceClient(addr, hostName, c.redisClient)
	if err != nil {
		return errs.New(err)
	}

	clientWithReferenceCount := &myTelegramReaderServiceClientWithReferenceCount{
		MyTelegramReaderServiceClient: client,
		referenceCountHeap:            &c.serviceClientWithSessionCountHeap,
		logger:                        c.logger,
	}

	err = c.syncReaderSessions(ctx, hostName, clientWithReferenceCount)
	if err != nil {
		return errs.New(err)
	}
	return nil
}

func (c *clientManager) syncReaderSessions(ctx context.Context, hostName string, client *myTelegramReaderServiceClientWithReferenceCount) error {
	onNew, onDelete, onError, closeFunc := c.dal.SubscribeTelegramReaderSessionChange(ctx, hostName)
	client.addOnClose(func(ctx context.Context) error {
		err := closeFunc()
		if err != nil {
			return errs.New(err)
		}
		return nil
	})

	go func() {
		for {
			select {
			case newSessionIDs, ok := <-onNew:
				if !ok {
					return
				}
				for _, sessionID := range newSessionIDs {
					c.storeSessionIDToClient(hostName, sessionID, client)
				}

			case deletedSessionIDs, ok := <-onDelete:
				if !ok {
					return
				}
				for _, sessionID := range deletedSessionIDs {
					c.removeSessionIDToClient(hostName, sessionID)
				}
			case err, ok := <-onError:
				if !ok {
					return
				}
				c.logger.Errorf("error when reading SubscribeTelegramReaderChange: %v", errs.New(err))
			}
		}
	}()
	return nil
}

func (c *clientManager) storeSessionIDToClient(hostName string, sessionID string, client *myTelegramReaderServiceClientWithReferenceCount) {
	c.appendHostNameToSessionID(hostName, sessionID)
	oldClient, loaded := c.sessionIDToClientMap.LoadOrStore(sessionID, client)
	client.AddSessionCount()
	if loaded {
		c.logger.Errorf("sessionID %s already exists, replacing with new client", sessionID)
		theOldClient := oldClient.(*myTelegramReaderServiceClientWithReferenceCount)
		theOldClient.DeductSessionCount()
	}
}

func (c *clientManager) removeSessionIDToClient(hostName string, sessionID string) {
	oldClient, loaded := c.sessionIDToClientMap.LoadAndDelete(sessionID)
	if loaded {
		theOldClient := oldClient.(*myTelegramReaderServiceClientWithReferenceCount)
		remainReferenceCount := theOldClient.DeductSessionCount()
		if remainReferenceCount == 0 {
			c.removeHostName(hostName)
		} else {
			c.removeHostNameToSessionID(hostName, sessionID)
		}
	}
	c.logger.Errorf("tring to remove sessionID %s, but not found in sessionIDToClientMap", sessionID)
}

func (c *clientManager) appendHostNameToSessionID(hostName string, sessionID string) {
	sessonIDMap := sync.Map{}
	sessonIDMap.Store(sessionID, struct{}{})
	existIDMap, loaded := c.hostNameToSessionID.LoadOrStore(hostName, &sessonIDMap)
	if loaded {
		// 如果已經存在，則將新的 sessionID 添加到現有的映射中
		existIDMap.(*sync.Map).Store(sessionID, struct{}{})
		return
	}
}

func (c *clientManager) removeHostNameToSessionID(hostName string, sessionID string) {
	existIDMap, loaded := c.hostNameToSessionID.Load(hostName)
	if loaded {
		existIDMap.(*sync.Map).Delete(sessionID)
		return
	}
	c.logger.Errorf("hostName %s not found in hostNameToSessionID map", hostName)
}

func (c *clientManager) removeHostName(hostName string) {
	sessionMap, loaded := c.hostNameToSessionID.LoadAndDelete(hostName)
	if !loaded {
		c.logger.Errorf("hostName %s not found in hostNameToSessionID map", hostName)
		return
	}
	sessionCount := 0
	sessionMap.(*sync.Map).Range(func(key, value interface{}) bool {
		sessionCount++
		return true
	})
	if sessionCount != 1 {
		c.logger.Errorf("sessionCount %d != 1, hostName %s", sessionCount, hostName)
	}
}

type myTelegramReaderServiceClientWithReferenceCount struct {
	MyTelegramReaderServiceClient
	referenceCountHeap *telegramReaderServiceClientHeap
	referenceCount     atomic.Uint32
	logger             log.Logger
}

func (m *myTelegramReaderServiceClientWithReferenceCount) addOnClose(f func(ctx context.Context) error) {
	//TODO implement me
	panic("implement me")
}

func (m *myTelegramReaderServiceClientWithReferenceCount) DeductSessionCount() uint32 {
	if m.referenceCount.Load() == 0 {
		// close MyTelegramReaderServiceClient and remove self from heap
		err := m.Close(context.Background())
		if err != nil {
			m.logger.Errorf("error when closing client: %v", errs.New(err))
		}
		m.referenceCountHeap.Remove(m)
		return 0
	}
	return m.referenceCount.Add(^uint32(0))
}

func (m *myTelegramReaderServiceClientWithReferenceCount) SetSessionCount(newVal uint32) {
	m.referenceCount.Store(newVal)
}

func (m *myTelegramReaderServiceClientWithReferenceCount) AddSessionCount() uint32 {
	return m.referenceCount.Add(1)
}

// telegramReaderServiceClientHeap 定義一個整數切片，實作 heap.Interface
// 用來取得最少 session count 的 client
type telegramReaderServiceClientHeap struct {
	slice []*myTelegramReaderServiceClientWithReferenceCount
	lock  sync.Mutex
	index map[*myTelegramReaderServiceClientWithReferenceCount]int
}

// 以下四個方法構成 heap.Interface 的必要實作

func (h *telegramReaderServiceClientHeap) Len() int { return len(h.slice) }
func (h *telegramReaderServiceClientHeap) Less(i, j int) bool {
	h.lock.Lock()
	defer h.lock.Unlock()
	return h.slice[i].referenceCount.Load() < h.slice[j].referenceCount.Load()
} // 小頂堆：h[i] < h[j]
// 如果想要大頂堆，改為 h[i] > h[j]

func (h *telegramReaderServiceClientHeap) Swap(i, j int) {
	h.lock.Lock()
	defer h.lock.Unlock()
	h.slice[i], h.slice[j] = h.slice[j], h.slice[i]
	// 同步更新映射
	h.index[h.slice[i]] = i
	h.index[h.slice[j]] = j
}

// Push 和 Pop 使用指標接收者，以便修改底層切片
func (h *telegramReaderServiceClientHeap) Push(x interface{}) {
	h.lock.Lock()
	defer h.lock.Unlock()
	h.slice = append(h.slice, x.(*myTelegramReaderServiceClientWithReferenceCount))
	h.index[x.(*myTelegramReaderServiceClientWithReferenceCount)] = len(h.slice) - 1
}

func (h *telegramReaderServiceClientHeap) Pop() interface{} {
	h.lock.Lock()
	defer h.lock.Unlock()
	old := h.slice
	n := len(old)
	x := old[n-1]
	h.slice = old[:n-1]
	delete(h.index, x)
	return x
}

func (h *telegramReaderServiceClientHeap) Remove(v *myTelegramReaderServiceClientWithReferenceCount) bool {
	h.lock.Lock()
	defer h.lock.Unlock()

	i, ok := h.index[v]
	if !ok {
		return false
	}
	heap.Remove(h, i)
	return true
}

func NewClientManager(ctx context.Context, redisClient redis.UniversalClient, logger log.Logger) (ClientManager, error) {
	manager := &clientManager{
		redisClient: redisClient,
		logger:      logger,
		serviceClientWithSessionCountHeap: telegramReaderServiceClientHeap{
			index: make(map[*myTelegramReaderServiceClientWithReferenceCount]int),
		},
	}
	err := manager.syncReaders(ctx)
	if err != nil {
		return nil, errs.New(err)
	}
	return manager, nil
}
