package module

import (
	"core/log"
	"time"
)

type Collector struct {
	Logger log.Logger
}

func (c *Collector) Collect(text string, messageTime time.Time) error {

}
