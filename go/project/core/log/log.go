package log

import (
	"context"
	"core/env"
	"core/errs"
	"core/graceful_shutdown"
	"github.com/sirupsen/logrus"
	"io"
	"os"
	"sync/atomic"
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
	file *os.File
}

func (l *logger) WithFields(fields logrus.Fields) Logger {
	return &logger{
		FieldLogger: l.FieldLogger.WithFields(fields),
		file:        l.file,
	}
}

func (l *logger) WithField(key string, value interface{}) Logger {
	return &logger{
		FieldLogger: l.FieldLogger.WithField(key, value),
		file:        l.file,
	}
}

func (l *logger) WithError(err error) Logger {
	return &logger{
		FieldLogger: l.FieldLogger.WithError(err),
		file:        l.file,
	}
}

func (l *logger) Close() error {
	if l.file == nil {
		return nil
	}
	err := l.file.Sync()
	if err != nil {
		return errs.New("Failed to sync log file error: %v", err)
	}
	err = l.file.Close()
	if err != nil {
		return errs.New("Failed to close log file error: %v", err)
	}
	return nil
}

const (
	logFileFlag             = os.O_APPEND | os.O_CREATE | os.O_WRONLY
	logFilePerm os.FileMode = 0644
)

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
	// convert string to logrus level
	level, err := logrus.ParseLevel(string(logLevel))
	if err != nil {
		log.Fatalf("Failed to parse log level because %v", err)
	}
	log.SetLevel(level)

	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})

	file, err := os.OpenFile(logPath, logFileFlag, logFilePerm)
	if err != nil {
		log.Fatalf("Failed to initialize log file because %v", err)
	}

	writers := []io.Writer{
		file,
		os.Stdout,
	}

	outWriter := io.MultiWriter(writers...)

	log.SetOutput(outWriter)

	newLogger := &logger{
		FieldLogger: log.WithFields(logrus.Fields{}),
		file:        file,
	}

	graceful_shutdown.AddFinalizer(func(ctx context.Context) {
		err1 := newLogger.Close()
		if err1 != nil {
			logrus.Errorf("fail to close logger: %v, logPath: %s", err1, logPath)
		} else {
			logrus.Infof("logger closed: %s", logPath)
		}
	})
	return newLogger
}
