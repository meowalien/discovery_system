package core

import "github.com/sirupsen/logrus"

func NewLogger(level logrus.Level, logPath string) logrus.FieldLogger {
	log := logrus.New()

	return log.WithFields(logrus.Fields{
		"level": level,
	})
}
