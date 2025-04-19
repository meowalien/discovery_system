package gincontext

import (
	"github.com/gin-gonic/gin"
	"go-root/lib/log"
	"time"
)

type contextKey[T any] string

func (cc contextKey[T]) Get(c *gin.Context) T {
	return c.MustGet(string(cc)).(T)
}

func (cc contextKey[T]) Set(c *gin.Context, t T) {
	c.Set(string(cc), t)
}

const (
	Logger           contextKey[log.Logger] = "Logger"
	TraceID          contextKey[string]     = "TraceID"
	RequestStartTime contextKey[time.Time]  = "RequestStartTime"
)
