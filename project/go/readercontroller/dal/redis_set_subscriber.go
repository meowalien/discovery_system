package dal

import (
	"context"
	"errors"
	"github.com/redis/go-redis/v9"
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
	sessions, err := s.dal.readSessions(ctx, s.sessionKey)
	if err != nil {
		return err
	}
	for _, sess := range sessions {
		s.sessionCache[sess] = struct{}{}
	}

	// 發送初始資料
	s.newCh <- sessions

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

		s.handlePayload(msg.Payload)
	}
}

// handlePayload 根據 Redis 事件觸發更新
func (s *redisSetSubscriber) handlePayload(payload string) {
	sessList, err := s.dal.readSessions(context.Background(), s.sessionKey)
	if err != nil {
		s.errCh <- err
		return
	}
	added, removed, newCache := s.dal.diffKeys(s.sessionCache, sessList)
	if len(added) > 0 {
		hosts, err := s.dal.parseHostNameFromKeys(added)
		if err != nil {
			s.errCh <- err
		} else {
			s.newCh <- hosts
		}
	}
	if len(removed) > 0 {
		hosts, err := s.dal.parseHostNameFromKeys(removed)
		if err != nil {
			s.errCh <- err
		} else {
			s.delCh <- hosts
		}
	}
	// 更新快取
	s.sessionCache = newCache
}

// close 結束訂閱
func (s *redisSetSubscriber) close() error {
	err := s.pubsub.Close()
	s.closeChannels()
	return err
}

func (s *redisSetSubscriber) closeChannels() {
	close(s.newCh)
	close(s.delCh)
	close(s.errCh)
}
