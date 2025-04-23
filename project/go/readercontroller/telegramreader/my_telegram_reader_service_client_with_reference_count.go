package telegramreader

import (
	"context"
	"go-root/lib/errs"
	"go-root/lib/log"
	"sync/atomic"
)

type myTelegramReaderServiceClientWithReferenceCount struct {
	MyTelegramReaderServiceClient
	referenceCountHeap TelegramReaderServiceClientHeap
	referenceCount     atomic.Uint32
	logger             log.Logger
	onCloseCallback    []func(ctx context.Context) error
}

func (m *myTelegramReaderServiceClientWithReferenceCount) GetReferenceCount() uint32 {
	return m.referenceCount.Load()
}

func (m *myTelegramReaderServiceClientWithReferenceCount) AddOnClose(f func(ctx context.Context) error) {
	m.onCloseCallback = append(m.onCloseCallback, f)
}

func (m *myTelegramReaderServiceClientWithReferenceCount) Close(ctx context.Context) error {
	var err error
	// iterate m.onCloseCallback in reverse order
	for i := len(m.onCloseCallback) - 1; i >= 0; i-- {
		f := m.onCloseCallback[i]
		e := f(ctx)
		if e != nil {
			if err != nil {
				err = errs.New("%w; %v", err, e)
			} else {
				err = e
			}
		}
	}
	e := m.MyTelegramReaderServiceClient.Close(ctx)
	if e != nil {
		if err != nil {
			err = errs.New("%w; %v", err, e)
		} else {
			err = e
		}
	}
	return err
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

type MyTelegramReaderServiceClientWithReferenceCount interface {
	MyTelegramReaderServiceClient
	AddOnClose(func(ctx context.Context) error)
	AddSessionCount() uint32
	DeductSessionCount() uint32
	GetReferenceCount() uint32
}

func NewMyTelegramReaderServiceClientWithReferenceCount(client MyTelegramReaderServiceClient, referenceCountHeap TelegramReaderServiceClientHeap, logger log.Logger) MyTelegramReaderServiceClientWithReferenceCount {
	return &myTelegramReaderServiceClientWithReferenceCount{
		MyTelegramReaderServiceClient: client,
		referenceCountHeap:            referenceCountHeap,
		logger:                        logger,
	}
}
