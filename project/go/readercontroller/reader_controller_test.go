package readercontroller

import (
	"context"
	"github.com/sirupsen/logrus"
	"go-root/config"
	"go-root/lib/data_source"
	"go-root/lib/graceful_shutdown"
	"go-root/lib/log"
	"go-root/readercontroller/dal"
	"testing"
	"time"
)

var globalLogger log.Logger

func init() {
	globalLogger = log.NewLogger()
	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		e := globalLogger.Close()
		if e != nil {
			logrus.Errorf("logger close fail: %v", e)
		}
		logrus.Info("logger finalized")
	})
}

func setupController() ReaderController {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
	defer cancel()

	redisClient, err := data_source.NewRedisClient(ctx, config.GetConfig().Redis)
	db, err := data_source.NewGormDB(ctx, config.GetConfig().Postgres.DSN())
	if err != nil {
		globalLogger.Fatalf("failed to connect to database: %v", err)
	}

	dataAccessLayer := dal.NewDAL(db, redisClient)
	manager, err := NewClientManager(ctx, globalLogger, dataAccessLayer)
	if err != nil {
		globalLogger.Fatalf("failed to create client manager: %v", err)
	}
	return NewReaderController(dataAccessLayer, manager)
}

const (
	api_id     = 24529225
	api_hash   = "0abc06cc13bab8c228b59bcca4284800"
	session_id = "f5927a31-a521-48df-90ed-f71d19cd6998"
	password   = "kingkingjin"
	user_id    = "b3ab5439-b350-4ed7-9728-9436dd8c1e65"
)

func TestCreateClient(t *testing.T) {
	c := setupController()
	time.Sleep(time.Second * 5)

	sessionID, err := c.CreateClient(context.Background(), api_id, api_hash, user_id)
	if err != nil {
		t.Fatalf("failed to create client: %v", err)
	}
	if sessionID == "" {
		t.Fatalf("session ID is empty")
	}
	globalLogger.Infof("session ID: %s\n", sessionID)
}
