package graceful_shutdown

import (
	"context"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

type gracefulShutdownQueue struct {
	mutex sync.Mutex
	queue []func(ctx context.Context)
}

func (g *gracefulShutdownQueue) AddFinalizer(f func(ctx context.Context)) {
	g.mutex.Lock()
	defer g.mutex.Unlock()
	g.queue = append(g.queue, f)
}

func (g *gracefulShutdownQueue) WaitForShutdown(shutdownDeadline time.Duration) {
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit
	queue.RunFinalizers(shutdownDeadline)
}

func (g *gracefulShutdownQueue) RunFinalizers(shutdownDeadline time.Duration) {
	g.mutex.Lock()
	defer g.mutex.Unlock()
	ctx, cancel := context.WithTimeout(context.Background(), shutdownDeadline)
	defer cancel()
	for i := len(g.queue) - 1; i >= 0; i-- {
		g.queue[i](ctx)
	}
}

var queue = &gracefulShutdownQueue{}

func AddFinalizer(f func(ctx context.Context)) {
	queue.AddFinalizer(f)
}

func WaitForShutdown(shutdownDeadline time.Duration) {
	queue.WaitForShutdown(shutdownDeadline)
}

//
//func RunFinalizers(shutdownDeadline time.Duration) {
//	queue.RunFinalizers(shutdownDeadline)
//}
