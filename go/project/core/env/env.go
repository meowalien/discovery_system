package env

import (
	"github.com/joho/godotenv"
	"github.com/kelseyhightower/envconfig"
	"github.com/sirupsen/logrus"
	"sync/atomic"
)

type Env struct {
	Port          string   `envconfig:"PORT" default:"3000"`
	LogLevel      LogLevel `envconfig:"LOG_LEVEL" default:"info"`
	LogFile       string   `envconfig:"LOG_FILE" default:"./out.log"`
	AccessLogFile string   `envconfig:"ACCESS_LOG_FILE" default:"./access.log"`
	Version       string   `envconfig:"VERSION" default:"unknown"`
	Mode          Mode     `envconfig:"MODE" default:"debug"`
}

type LogLevel string

const (
	LogLevelPanic   LogLevel = "panic"
	LogLevelFatal   LogLevel = "fatal"
	LogLevelError   LogLevel = "error"
	LogLevelWarning LogLevel = "warning"
	LogLevelInfo    LogLevel = "info"
	LogLevelDebug   LogLevel = "debug"
	LogLevelTrace   LogLevel = "trace"
)

type Mode string

const (
	ModeDebug   Mode = "debug"
	ModeRelease Mode = "release"
)

func checkEnv(e Env) {
	switch e.Mode {
	case ModeDebug, ModeRelease:
	default:
		logrus.Fatalf("invalid mode: %s", e.Mode)
	}

	switch e.LogLevel {
	case LogLevelPanic, LogLevelFatal, LogLevelError, LogLevelWarning, LogLevelInfo, LogLevelDebug, LogLevelTrace:
	default:
		logrus.Fatalf("invalid log level: %s", e.LogLevel)
	}
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
	// Load .env file if exists
	if err := godotenv.Load(".env"); err != nil {
		logrus.Warnf("No .env file found, using system environment variables")
	}

	err := envconfig.Process("", cfg)
	if err != nil {
		logrus.Fatalf("envconfig.Process error: %v", err)
	}
}

func InitEnv() {
	var e Env
	loadEnv(&e)
	checkEnv(e)
	env.Store(&e)
}
