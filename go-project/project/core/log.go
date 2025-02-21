package core

import (
	"github.com/sirupsen/logrus"
	"io"
	"os"
	"sync"
	"sync/atomic"
)

const (
	logFileFlag             = os.O_APPEND | os.O_CREATE | os.O_WRONLY
	logFilePerm os.FileMode = 0644
)

var openFiles = sync.Map{}

var globalLogger atomic.Pointer[logrus.FieldLogger]

func SetGlobalLogger(l logrus.FieldLogger) {
	globalLogger.Store(&l)
}

func GetGlobalLogger() logrus.FieldLogger {
	l := globalLogger.Load()
	if l == nil {
		logrus.Errorf("Global logger is nil")
		return logrus.New()
	}
	return *l
}

func NewLogger(levelStr string, logPath string) logrus.FieldLogger {
	log := logrus.New()
	// convert string to logrus level
	level, err := logrus.ParseLevel(levelStr)
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
	_, loaded := openFiles.Swap(logPath, file)
	if loaded {
		log.Fatalf("Log file %s is already opened by another logger", logPath)
	}

	writers := []io.Writer{
		file,
		os.Stdout,
	}

	outWriter := io.MultiWriter(writers...)

	log.SetOutput(outWriter)

	return log.WithFields(logrus.Fields{})
}

func FinalizeLoggers() {
	openFiles.Range(func(key, value interface{}) bool {
		file := value.(*os.File)
		err := file.Sync()
		if err != nil {
			logrus.Errorf("Failed to sync log file %s because %v", key, err)
		}
		err = file.Close()
		if err != nil {
			logrus.Errorf("Failed to close log file %s because %v", key, err)
		}
		return true
	})
}
