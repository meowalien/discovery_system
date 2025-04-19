package context_value

import (
	"context"
	"go-root/lib/log"
)

type contextKey[T any] string

func (cc contextKey[T]) Get(c context.Context) T {
	return c.Value(cc).(T)
}

func (cc contextKey[T]) Set(c context.Context, t T) context.Context {
	return context.WithValue(c, cc, t)
}

const (
	Logger contextKey[log.Logger] = "Logger"
)
