package core

import (
	"context"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

type GracefulShutdownQueue interface {
	Register(f func(ctx context.Context))
	WaitForShutdown()
	Run(shutdownDeadline time.Duration)
}

type gracefulShutdownQueue struct {
	mutex sync.Mutex
	queue []func(ctx context.Context)
}

func (g *gracefulShutdownQueue) Register(f func(ctx context.Context)) {
	g.mutex.Lock()
	defer g.mutex.Unlock()
	g.queue = append(g.queue, f)
}

func (g *gracefulShutdownQueue) WaitForShutdown() {
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit
}

func (g *gracefulShutdownQueue) Run(shutdownDeadline time.Duration) {
	ctx, cancel := context.WithTimeout(context.Background(), shutdownDeadline)
	defer cancel()
	for i := len(g.queue) - 1; i >= 0; i-- {
		g.queue[i](ctx)
	}
}

func NewGracefulShutdownQueue() GracefulShutdownQueue {
	return &gracefulShutdownQueue{}
}
