package core

import (
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
	"sync/atomic"
)

type Config struct {
	Version string `mapstructure:"version"`
}

var config atomic.Pointer[Config]

func GetConfig() Config {
	c := config.Load()
	if c == nil {
		logrus.Fatalf("config is nil")
	}
	return *c
}

func loadConfig(c any) {
	// 設定 viper 読取路徑與檔名
	viper.SetConfigName("config")
	viper.AddConfigPath("conf")
	viper.SetConfigType("yaml")

	// 讀取檔案
	err := viper.ReadInConfig()
	if err != nil {
		logrus.Fatalf("讀取 config.yaml 失敗: %v", err)
	}

	// mapstructure 會將讀取的設定檔轉換成 struct
	err = viper.Unmarshal(c)
	if err != nil {
		logrus.Fatalf("解析 config.yaml 失敗: %v", err)
	}
}

func InitConfig() {
	c := &Config{}
	loadConfig(c)
	config.Store(c)
}
