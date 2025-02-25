package log

import (
	"context"
	"core/env"
	"core/graceful_shutdown"
	rotatelogs "github.com/lestrrat-go/file-rotatelogs"
	"github.com/sirupsen/logrus"
	"io"
	"os"
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
	return nil // 使用 rotatelogs 無需手動關閉文件
}

func SetGlobalLogger(l Logger) {
	logrus.SetLevel(l.GetLevel())
	logrus.SetOutput(io.MultiWriter([]io.Writer{
		l.GetFile(),
		os.Stdout,
	}...))
	logrus.SetFormatter(l.GetFormatter())
}

func NewLogger(logLevel env.LogLevel, logPath string) Logger {
	log := logrus.New()
	// 轉換字串到 logrus Level
	level, err := logrus.ParseLevel(string(logLevel))
	if err != nil {
		log.Fatalf("Failed to parse log level because %v", err)
	}
	log.SetLevel(level)
	formatter := logrus.TextFormatter{
		FullTimestamp: true,
	}
	logrus.SetFormatter(&formatter)

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
		logLevel:    level,
		formatter:   &formatter,
		FieldLogger: log.WithFields(logrus.Fields{}),
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
