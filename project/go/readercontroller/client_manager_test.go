package readercontroller_test

import (
	"context"
	"github.com/google/uuid"
	"go-root/readercontroller/dal"
	"testing"
	"time"

	"go-root/lib/log"
	"go-root/readercontroller"
)

// fakeDAL implements dal.DAL with no-op channels
type fakeDAL struct{}

func (f *fakeDAL) GetSessionIDsByUserName(ctx context.Context, userID string) ([]uuid.UUID, error) {
	//TODO implement me
	panic("implement me")
}

func (f *fakeDAL) CreateTelegramClient(ctx context.Context, client dal.TelegramClient) error {
	//TODO implement me
	panic("implement me")
}

func (f *fakeDAL) CheckIfSessionExist(ctx context.Context, sessionID string, userID string) (bool, error) {
	//TODO implement me
	panic("implement me")
}

func (f *fakeDAL) SubscribeTelegramReaderChange(ctx context.Context) (<-chan []string, <-chan []string, <-chan error, func() error) {
	newCh := make(chan []string)
	deleteCh := make(chan []string)
	errCh := make(chan error)

	go func() {
		newCh <- []string{"newReader1"}
		newCh <- []string{"newReader2"}
		time.Sleep(time.Second * 3)
		deleteCh <- []string{"newReader2"}
		newCh <- []string{"newReader3"}
	}()

	return newCh, deleteCh, errCh, func() error { return nil }
}

func (f *fakeDAL) SubscribeTelegramReaderSessionChange(ctx context.Context, hostName string) (<-chan []string, <-chan []string, <-chan error, func() error) {
	newCh := make(chan []string)
	deleteCh := make(chan []string)
	errCh := make(chan error)

	if hostName == "newReader1" {
		go func() {
			newCh <- []string{"session1"}
			newCh <- []string{"session2"}
			time.Sleep(time.Second)
			deleteCh <- []string{"session2"}
			newCh <- []string{"session3"}
		}()
	}

	return newCh, deleteCh, errCh, func() error { return nil }
}

func TestNewClientManager(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	logger := log.NewLogger()
	d := &fakeDAL{}

	mgr, err := readercontroller.NewClientManager(ctx, logger, d)
	if err != nil {
		t.Fatalf("NewClientManager returned error: %v", err)
	}
	if mgr == nil {
		t.Fatal("NewClientManager returned nil manager")
	}
	time.Sleep(time.Second * 10)
	err = mgr.Close(context.Background())
	if err != nil {
		t.Fatalf("NewClientManager returned error: %v", err)
	}
}

func TestFindAvailableClient_NoClient(t *testing.T) {
	ctx := context.Background()
	logger := log.NewLogger()
	d := &fakeDAL{}
	mgr, _ := readercontroller.NewClientManager(ctx, logger, d)

	_, err := mgr.FindAvailableClient(ctx)
	if err == nil {
		t.Fatal("Expected error when no client available, got nil")
	}
}

func TestFindClientBySessionID_NotFound(t *testing.T) {
	ctx := context.Background()
	logger := log.NewLogger()
	d := &fakeDAL{}
	mgr, _ := readercontroller.NewClientManager(ctx, logger, d)

	cli, found, err := mgr.FindClientBySessionID(ctx, "nonexistent")
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if found {
		t.Fatalf("Expected found==false, got true, client: %v", cli)
	}
}

func TestClose(t *testing.T) {
	ctx := context.Background()
	logger := log.NewLogger()
	d := &fakeDAL{}
	mgr, _ := readercontroller.NewClientManager(ctx, logger, d)

	if err := mgr.Close(ctx); err != nil {
		t.Fatalf("Expected no error on Close, got %v", err)
	}
}
