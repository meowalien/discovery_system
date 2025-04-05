package gincontext

import (
	"core/log"
	"github.com/gin-gonic/gin"
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
