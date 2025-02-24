package log

import (
	"context"
	"core/env"
	"core/graceful_shutdown"
	rotatelogs "github.com/lestrrat-go/file-rotatelogs"
	"github.com/sirupsen/logrus"
	"io"
	"os"
	"sync/atomic"
	"time"
)

type Logger interface {
	WithFields(fields logrus.Fields) Logger
	WithField(key string, value interface{}) Logger
	WithError(err error) Logger

	Debugf(format string, args ...interface{})
	Infof(format string, args ...interface{})
	Printf(format string, args ...interface{})
	Warnf(format string, args ...interface{})
	Warningf(format string, args ...interface{})
	Errorf(format string, args ...interface{})
	Fatalf(format string, args ...interface{})
	Panicf(format string, args ...interface{})

	Debug(args ...interface{})
	Info(args ...interface{})
	Print(args ...interface{})
	Warn(args ...interface{})
	Warning(args ...interface{})
	Error(args ...interface{})
	Fatal(args ...interface{})
	Panic(args ...interface{})

	Debugln(args ...interface{})
	Infoln(args ...interface{})
	Println(args ...interface{})
	Warnln(args ...interface{})
	Warningln(args ...interface{})
	Errorln(args ...interface{})
	Fatalln(args ...interface{})
	Panicln(args ...interface{})
	Close() error
}

type logger struct {
	logrus.FieldLogger
}

func (l *logger) WithFields(fields logrus.Fields) Logger {
	return &logger{
		FieldLogger: l.FieldLogger.WithFields(fields),
	}
}

func (l *logger) WithField(key string, value interface{}) Logger {
	return &logger{
		FieldLogger: l.FieldLogger.WithField(key, value),
	}
}

func (l *logger) WithError(err error) Logger {
	return &logger{
		FieldLogger: l.FieldLogger.WithError(err),
	}
}

func (l *logger) Close() error {
	return nil // 使用 rotatelogs 無需手動關閉文件
}

var globalLogger atomic.Pointer[Logger]

func SetGlobalLogger(l Logger) {
	globalLogger.Store(&l)
}

func GetGlobalLogger() Logger {
	l := globalLogger.Load()
	if l == nil {
		logrus.Errorf("Global logger is nil")
		return &logger{
			FieldLogger: logrus.New(),
		}
	}
	return *l
}

func NewLogger(logLevel env.LogLevel, logPath string) Logger {
	log := logrus.New()
	// 轉換字串到 logrus Level
	level, err := logrus.ParseLevel(string(logLevel))
	if err != nil {
		log.Fatalf("Failed to parse log level because %v", err)
	}
	log.SetLevel(level)

	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})

	// 設置 rotatelogs
	logWriter, err := rotatelogs.New(
		logPath+"-%Y-%m-%d.log",
		rotatelogs.WithMaxAge(7*24*time.Hour),     // 最長保留 7 天
		rotatelogs.WithRotationTime(24*time.Hour), // 每 24 小時輪轉一次
	)
	if err != nil {
		log.Fatalf("Failed to initialize rotatelogs because %v", err)
	}

	writers := []io.Writer{
		logWriter,
		os.Stdout,
	}

	outWriter := io.MultiWriter(writers...)
	log.SetOutput(outWriter)

	newLogger := &logger{
		FieldLogger: log.WithFields(logrus.Fields{}),
	}

	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		logrus.Infof("logger finalized: %s", logPath)
	})

	return newLogger
}
