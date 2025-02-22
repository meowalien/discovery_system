package core

import (
	"core/errs"
	"github.com/sirupsen/logrus"
	"io"
	"os"
	"sync/atomic"
)

type Logger interface {
	logrus.FieldLogger
	Close() error
}

type logger struct {
	logrus.FieldLogger
	file *os.File
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

func NewLogger(logLevel LogLevel, logPath string) Logger {
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

	return &logger{
		FieldLogger: log.WithFields(logrus.Fields{}),
		file:        file,
	}
}
