package config

import (
	"fmt"
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
	"reflect"
	"sync/atomic"
)

type Config struct {
	Qdrant struct {
		Host   string `mapstructure:"host"`
		Port   int    `mapstructure:"port"`
		APIKey string `mapstructure:"api_key"`
	} `mapstructure:"qdrant"`
	EmbeddingService struct {
		Host string `mapstructure:"host"`
		Port int    `mapstructure:"port"`
	} `mapstructure:"embedding_service"`
}

var config atomic.Pointer[Config]

func GetConfig() Config {
	c := config.Load()
	if c == nil {
		logrus.Fatalf("config is nil")
	}
	return *c
}

func InitConfig() {
	c := &Config{}
	loadConfig(c)
	config.Store(c)
}

// 遞迴檢查 struct 是否所有欄位都出現在 config.yaml 內
func validateConfigStructure(prefix string, configType reflect.Type) error {
	for i := 0; i < configType.NumField(); i++ {
		field := configType.Field(i)
		configKey := field.Tag.Get("mapstructure")

		if configKey == "" {
			continue // 沒有 `mapstructure` tag 就跳過
		}

		// 組合完整 key，例如 `database.host`
		fullKey := configKey
		if prefix != "" {
			fullKey = prefix + "." + configKey
		}

		// 確保 key 存在於 `config.yaml`
		if !viper.IsSet(fullKey) {
			return fmt.Errorf("config.yaml missing key: %s", fullKey)
		}

		// 若欄位是 struct，則遞迴檢查
		if field.Type.Kind() == reflect.Struct {
			if err := validateConfigStructure(fullKey, field.Type); err != nil {
				return err
			}
		}

		// 若欄位是 slice 且元素是 struct，則檢查 slice 內的 struct
		if field.Type.Kind() == reflect.Slice && field.Type.Elem().Kind() == reflect.Struct {
			if err := validateConfigStructure(fullKey+"[*]", field.Type.Elem()); err != nil {
				return err
			}
		}

		// 若欄位是 map 且 value 是 struct，則檢查 map 內的 struct
		if field.Type.Kind() == reflect.Map && field.Type.Elem().Kind() == reflect.Struct {
			if err := validateConfigStructure(fullKey+"{*}", field.Type.Elem()); err != nil {
				return err
			}
		}
	}
	return nil
}

func loadConfig(c any) {
	// 設定 viper 読取路徑與檔名
	viper.SetConfigName("config")
	viper.AddConfigPath("conf")
	viper.SetConfigType("yaml")

	// 讀取檔案
	err := viper.ReadInConfig()
	if err != nil {
		logrus.Fatalf("failed to read config.yaml: %v", err)
	}
	// mapstructure 會將讀取的設定檔轉換成 struct
	err = viper.Unmarshal(c)
	if err != nil {
		logrus.Fatalf("failed to unmarshal config: %v", err)
	}
	// 確保所有 struct 中的欄位都有在 config.yaml 中定義
	err = validateConfigStructure("", reflect.TypeOf(c).Elem())
	if err != nil {
		logrus.Fatalf("wrong config structure: %v", err)
	}
}
