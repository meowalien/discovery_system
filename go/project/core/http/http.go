package http

import (
	"context"
	"core/env"
	"core/log"
	"errors"
	"github.com/gin-gonic/gin"
	"net/http"
	"sync/atomic"
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
		Addr:    addr,
		Handler: h.engine,
	}
	swapped := h.server.CompareAndSwap(nil, srv)
	if !swapped {
		return errors.New("server already started")
	}

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
