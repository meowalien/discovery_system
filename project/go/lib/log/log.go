package log

import (
	"context"
	"fmt"
	rotatelogs "github.com/lestrrat-go/file-rotatelogs"
	"github.com/sirupsen/logrus"
	"go-root/lib/env"
	"go-root/lib/graceful_shutdown"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"time"
)

type Logger interface {
	GetLevel() logrus.Level
	GetFile() io.WriteCloser
	GetFormatter() logrus.Formatter

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
	logLevel  logrus.Level
	logFile   *rotatelogs.RotateLogs
	formatter logrus.Formatter
}

func (l *logger) GetLevel() logrus.Level {
	return l.logLevel
}

func (l *logger) GetFile() io.WriteCloser {
	return l.logFile
}

func (l *logger) GetFormatter() logrus.Formatter {
	return l.formatter
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
	return l.logFile.Close()
}

func NewLogger() Logger {
	logLevel, logPath := env.GetEnv().LogLevel, env.GetEnv().LogFile
	newLog := logrus.New()
	// 轉換字串到 logrus Level
	level, err := logrus.ParseLevel(string(logLevel))
	if err != nil {
		newLog.Fatalf("Failed to parse newLog level because %v", err)
	}
	newLog.SetLevel(level)
	newLog.SetReportCaller(true)
	formatter := logrus.TextFormatter{
		FullTimestamp: true,
		CallerPrettyfier: func(frame *runtime.Frame) (function string, file string) {
			//funcName := filepath.Base(frame.Function)
			fileLine := fmt.Sprintf("%s:%d", filepath.Base(frame.File), frame.Line)
			return "", fileLine
		},
	}
	newLog.SetFormatter(&formatter)

	// 設置 rotatelogs
	logWriter, err := rotatelogs.New(
		logPath+"-%Y-%m-%d.log",
		rotatelogs.WithMaxAge(7*24*time.Hour),     // 最長保留 7 天
		rotatelogs.WithRotationTime(24*time.Hour), // 每 24 小時輪轉一次
	)
	if err != nil {
		newLog.Fatalf("Failed to initialize rotatelogs because %v", err)
	}

	writers := []io.Writer{
		logWriter,
		os.Stdout,
	}

	outWriter := io.MultiWriter(writers...)
	newLog.SetOutput(outWriter)

	newLogger := &logger{
		logFile:     logWriter,
		logLevel:    level,
		formatter:   &formatter,
		FieldLogger: newLog.WithFields(logrus.Fields{}),
	}

	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		e := newLogger.Close()
		if e != nil {
			logrus.Errorf("logger close fail: %v", e)
		}
		logrus.Infof("logger finalized: %s", logPath)
	})

	return newLogger
}
