package core

import (
	"github.com/kelseyhightower/envconfig"
	"github.com/sirupsen/logrus"
	"sync/atomic"
)

type Env struct {
	Port     string `envconfig:"PORT" default:"3000"`
	LogLevel string `envconfig:"LOG_LEVEL" default:"info"`
	LogFile  string `envconfig:"LOG_FILE" default:"./log.log"`
}

var env atomic.Pointer[Env]

func GetEnv() Env {
	e := env.Load()
	if e == nil {
		logrus.Fatalf("env is nil")
	}

	return *e

}

func loadEnv(cfg any) {
	err := envconfig.Process("", cfg)
	if err != nil {
		logrus.Fatalf("envconfig.Process error: %v", err)
	}
}

func InitEnv() {
	var e Env
	loadEnv(&e)
	env.Store(&e)
}
