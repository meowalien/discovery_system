package telegramreader

import (
	"context"
	"go-root/lib/errs"
	"go-root/lib/log"
	"sync/atomic"
)

type myTelegramReaderServiceClientWithReferenceCount struct {
	MyTelegramReaderServiceClient
	referenceCount  atomic.Uint32
	logger          log.Logger
	onCloseCallback []func(ctx context.Context) error
}

func (m *myTelegramReaderServiceClientWithReferenceCount) GetReferenceCount() uint32 {
	return m.referenceCount.Load()
}

func (m *myTelegramReaderServiceClientWithReferenceCount) AddOnClose(f func(ctx context.Context) error) {
	m.logger.Debug("Adding on-close callback")
	m.onCloseCallback = append(m.onCloseCallback, f)
}

func (m *myTelegramReaderServiceClientWithReferenceCount) Close(ctx context.Context) error {
	m.logger.Debug("Closing telegram reader service client")
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
	currentCount := m.referenceCount.Load()
	m.logger.Debug("Deducting session count, current count:", currentCount)

	if currentCount == 0 {
		return 0
	}
	newCount := m.referenceCount.Add(^uint32(0))
	m.logger.Debug("Session count deducted. New count:", newCount)
	return newCount
}

func (m *myTelegramReaderServiceClientWithReferenceCount) SetSessionCount(newVal uint32) {
	m.logger.Debug("Setting session count to:", newVal)
	m.referenceCount.Store(newVal)
}

func (m *myTelegramReaderServiceClientWithReferenceCount) AddSessionCount() uint32 {
	newCount := m.referenceCount.Add(1)
	m.logger.Debug("Session count incremented. New count:", newCount)
	return newCount
}

type MyTelegramReaderWithReferenceCount interface {
	MyTelegramReaderServiceClient
	AddOnClose(func(ctx context.Context) error)
	AddSessionCount() uint32
	DeductSessionCount() uint32
	GetReferenceCount() uint32
}

func NewMyTelegramReaderWithReferenceCount(client MyTelegramReaderServiceClient, logger log.Logger) MyTelegramReaderWithReferenceCount {
	return &myTelegramReaderServiceClientWithReferenceCount{
		MyTelegramReaderServiceClient: client,
		logger:                        logger,
	}
}
