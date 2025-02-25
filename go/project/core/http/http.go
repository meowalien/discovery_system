package http

import (
	"context"
	"core/env"
	"core/graceful_shutdown"
	"core/log"
	"errors"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"net/http"
	"sync/atomic"
	"time"
)

type HTTPEngine interface {
	Start(addr string) error
	Stop(ctx context.Context) error
	Mount(func(gin.IRoutes))
}

type httpEngine struct {
	engine *gin.Engine
	server atomic.Pointer[http.Server]
}

func (h *httpEngine) Start(addr string) error {
	srv := &http.Server{
		Addr:           addr,
		Handler:        h.engine,
		ReadTimeout:    10 * time.Second,
		WriteTimeout:   10 * time.Second,
		IdleTimeout:    30 * time.Second,
		MaxHeaderBytes: 1 << 20, // 限制 header 大小為 1MB
	}
	swapped := h.server.CompareAndSwap(nil, srv)
	if !swapped {
		return errors.New("server already started")
	}

	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		// stop http server gracefully when receive shutdown signal
		if err := h.Stop(ctx); err != nil {
			logrus.Errorf("fail to stop http server: %v", err)
		} else {
			logrus.Infof("http server stopped")
		}
	})

	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}

func (h *httpEngine) Stop(ctx context.Context) error {
	srv := h.server.Load()
	if srv == nil {
		return errors.New("server not started")
	}
	return srv.Shutdown(ctx)
}

func (h *httpEngine) Mount(f func(gin.IRoutes)) {
	f(h.engine)
}

func NewHttpEngine(mode env.Mode) HTTPEngine {
	switch mode {
	case env.ModeDebug:
		gin.SetMode(gin.DebugMode)
	case env.ModeRelease:
		gin.SetMode(gin.ReleaseMode)
	default:
		log.GetGlobalLogger().Fatalf("invalid mode: %s", mode)
	}

	return &httpEngine{
		engine: gin.Default(),
	}
}
