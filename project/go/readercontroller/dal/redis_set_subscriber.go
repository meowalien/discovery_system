package dal

import (
	"context"
	"errors"
	"fmt"
	"github.com/redis/go-redis/v9"
	"go-root/readercontroller/enum"
	"net"
	"time"
)

// redisSetSubscriber 封裝訂閱所需狀態
type redisSetSubscriber struct {
	dal          *dal
	sessionKey   string
	pubsub       *redis.PubSub
	sessionCache map[string]struct{}

	newCh chan<- []string
	delCh chan<- []string
	errCh chan<- error
}

// init 讀取當前所有 session 並發出新列表
func (s *redisSetSubscriber) init(ctx context.Context) error {
	// 讀取並緩存當前 sessions
	//sessions, err := s.dal.readSessions(ctx, s.sessionKey)
	//if err != nil {
	//	return err
	//}
	fmt.Println("sessionKey: ", s.sessionKey)
	//fmt.Println("sessions: ", sessions)
	//for _, sess := range sessions {
	//	s.sessionCache[sess] = struct{}{}
	//}

	//// 發送初始資料
	//s.newCh <- sessions

	s.syncKeys()
	// 建立 Redis 訂閱
	s.pubsub = s.dal.redisClient.PSubscribe(ctx, "__keyspace@0__:"+s.sessionKey)
	return nil
}

// listen 處理來自 Redis 的過濾與更新
func (s *redisSetSubscriber) listen() {
	for {
		msg, err := s.pubsub.ReceiveMessage(context.Background())
		if err != nil {
			if errors.Is(err, redis.ErrClosed) || errors.Is(err, net.ErrClosed) {
				s.closeChannels()
				return
			}
			s.errCh <- err
			time.Sleep(time.Second)
			continue
		}

		switch msg.Payload {
		case "sadd":
		case "srem":
		default:
			// 其他事件不處理
			continue
		}

		s.syncKeys()
	}
}

// diffKeys 計算新增與刪除的 keys，並回傳新的快取 map
func (s *redisSetSubscriber) diffKeys(
	oldMap map[string]struct{},
	newKeys []string,
) (added []string, removed []string, newMap map[string]struct{}) {
	newMap = make(map[string]struct{}, len(newKeys))
	for _, k := range newKeys {
		if k == enum.INIT_SESSION_NAME {
			continue
		}
		newMap[k] = struct{}{}
		if _, ok := oldMap[k]; !ok {
			added = append(added, k)
		}
	}
	for k := range oldMap {
		if _, ok := newMap[k]; !ok {
			removed = append(removed, k)
		}
	}
	return
}

// syncKeys 根據 Redis 事件觸發更新
func (s *redisSetSubscriber) syncKeys() {
	sessList, err := s.dal.readSessions(context.Background(), s.sessionKey)
	if err != nil {
		s.errCh <- err
		return
	}

	added, removed, newCache := s.diffKeys(s.sessionCache, sessList)
	if len(added) > 0 {
		//hosts, e := s.dal.parseHostNameFromKeys(added)
		//if e != nil {
		//	s.errCh <- e
		//} else {
		fmt.Println("add hosts: ", added)
		s.newCh <- added
		//}
	}
	if len(removed) > 0 {
		//hosts, e := s.dal.parseHostNameFromKeys(removed)
		//if e != nil {
		//	s.errCh <- e
		//} else {
		fmt.Println("removed hosts: ", removed)
		s.delCh <- removed
		//}
	}
	// 更新快取
	s.sessionCache = newCache
}

// close 結束訂閱
func (s *redisSetSubscriber) close() error {
	return s.pubsub.Close()
}

func (s *redisSetSubscriber) closeChannels() {
	close(s.newCh)
	close(s.delCh)
	close(s.errCh)
}
