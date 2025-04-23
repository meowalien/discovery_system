package dal

import (
	"context"
	"errors"
	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
	"go-root/lib/data_source"
	"go-root/lib/errs"
	"go-root/readercontroller/enum"
	"gorm.io/gorm"
	"time"
)

type DAL interface {
	GetSessionIDsByUserName(ctx context.Context, userID string) ([]uuid.UUID, error)
	CreateTelegramClient(ctx context.Context, client TelegramClient) error
	CheckIfSessionExist(ctx context.Context, sessionID string, userID string) (bool, error)

	SubscribeTelegramReaderChange(ctx context.Context) (onNew <-chan []string, onDelete <-chan []string, onError <-chan error, closeFunc func() error)
	SubscribeTelegramReaderSessionChange(ctx context.Context, hostName string) (onNew <-chan []string, onDelete <-chan []string, onError <-chan error, closeFunc func() error)
}

type dal struct {
	postgresSQL *gorm.DB
	redisClient redis.UniversalClient
}

// SubscribeTelegramReaderSessionChange 監聽 Redis 中的某個 Telegram Reader 中的telegram session 變更
func (d *dal) SubscribeTelegramReaderSessionChange(ctx context.Context, hostName string) (
	onNew <-chan []string,
	onDelete <-chan []string,
	onError <-chan error,
	closeFunc func() error,
) {
	newCh := make(chan []string, 1)
	delCh := make(chan []string, 1)
	errCh := make(chan error, 1)

	subscriber := &redisSetSubscriber{
		dal:          d,
		sessionKey:   data_source.MakeKey(enum.REDIS_KEY_PREFIX_TELEGRAM_READER_SESSIONS, hostName),
		sessionCache: make(map[string]struct{}),
		newCh:        newCh,
		delCh:        delCh,
		errCh:        errCh,
	}

	// 初始化快取與首波通知
	if err := subscriber.init(ctx); err != nil {
		errCh <- err
	}

	// 啟動監聽協程
	go subscriber.listen()

	return newCh, delCh, errCh, subscriber.close
}

// SubscribeTelegramReaderChange 監聽 Redis 中的 Telegram Reader 變更
func (d *dal) SubscribeTelegramReaderChange(ctx context.Context) (
	onNew <-chan []string,
	onDelete <-chan []string,
	onError <-chan error,
	closeFunc func() error,
) {
	newCh := make(chan []string, 1)
	delCh := make(chan []string, 1)
	errCh := make(chan error, 1)

	subscriber := &redisSetSubscriber{
		dal:          d,
		sessionKey:   enum.REDIS_KEY_TELEGRAM_READERS,
		sessionCache: make(map[string]struct{}),
		newCh:        newCh,
		delCh:        delCh,
		errCh:        errCh,
	}

	// 初始化快取與首波通知
	if err := subscriber.init(ctx); err != nil {
		errCh <- err
	}

	// 啟動監聽協程
	go subscriber.listen()

	return newCh, delCh, errCh, subscriber.close
}

// 以下為 dal level 的輔助函式

// readSessions 從 Redis 取得所有 sessions
func (d *dal) readSessions(ctx context.Context, key string) ([]string, error) {
	c, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	sessions, err := d.redisClient.SMembers(c, key).Result()
	if err != nil {
		return nil, errs.New(err)
	}
	return sessions, nil
}

//// parseHostNameFromKey 解析 Redis key 為主機名稱
//func (d *dal) parseHostNameFromKey(key string) (string, error) {
//	parts := strings.Split(key, ":")
//	if len(parts) != 2 {
//		return "", fmt.Errorf("invalid key format: %s", key)
//	}
//	return parts[1], nil
//}

//// parseHostNameFromKeys 逐一解析多個 keys
//func (d *dal) parseHostNameFromKeys(keys []string) ([]string, error) {
//	hosts := make([]string, 0, len(keys))
//	for _, key := range keys {
//		h, err := d.parseHostNameFromKey(key)
//		if err != nil {
//			return nil, err
//		}
//		hosts = append(hosts, h)
//	}
//
//	return hosts, nil
//}

func (d *dal) CheckIfSessionExist(ctx context.Context, sessionID string, userID string) (bool, error) {
	err := d.postgresSQL.WithContext(ctx).Where("user_id = ? AND session_id = ?", userID, sessionID).Take(&TelegramClient{}).Error
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return false, nil
	}
	if err != nil {
		return false, errs.New(err)
	}
	return true, nil
}

func (d *dal) CreateTelegramClient(ctx context.Context, client TelegramClient) error {
	res := d.postgresSQL.Create(&client)
	if res.Error != nil {
		return errs.New(res.Error)
	}
	return nil
}

func (d *dal) GetSessionIDsByUserName(ctx context.Context, userID string) ([]uuid.UUID, error) {
	var sessions []uuid.UUID
	if err := d.postgresSQL.
		WithContext(ctx).
		Model(&TelegramClient{}).
		Where("user_id = ?", userID).
		Pluck("session_id", &sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}

func NewDAL(postgresSQL *gorm.DB, redisClient redis.UniversalClient) DAL {
	return &dal{postgresSQL: postgresSQL, redisClient: redisClient}
}
