package main

import (
	"core"
	"fmt"
	"github.com/gin-gonic/gin"
)

//// 全域變數儲存設定 (也可以包在 struct 裡)
//var (
//	version    string
//	qdrantHost string
//	qdrantPort int
//)
//
//func initConfig() {
//	// 設定 viper 読取路徑與檔名
//	viper.SetConfigName("config")
//	viper.SetConfigType("yaml")
//	viper.AddConfigPath(".")
//
//	// 讀取檔案
//	err := viper.ReadInConfig()
//	if err != nil {
//		logrus.Fatalf("讀取 config.yaml 失敗: %v", err)
//	}
//
//	// 取得版本資訊
//	version = viper.GetString("version")
//
//	// 取得 Qdrant 連線參數
//	qdrantHost = viper.GetString("qdrant.host")
//	qdrantPort = viper.GetInt("qdrant.port")
//}

func main() {
	core.InitEnv()
	core.InitConfig()
	defer core.FinalizeLoggers()
	globalLogger := core.NewLogger(core.GetEnv().LogLevel, core.GetEnv().LogFile)
	core.SetGlobalLogger(globalLogger)

	version := core.GetConfig().Version
	globalLogger.Infof("version: ", version)

	// 建立 Gin 引擎
	r := gin.Default()

	// 註冊 /version 路徑
	r.GET("/version", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"version": version,
		})
	})

	addr := fmt.Sprintf(":%s", core.GetEnv().Port)
	globalLogger.Infof("啟動 HTTP 伺服器，%s ...", addr)
	if err := r.Run(addr); err != nil {
		globalLogger.Fatalf("無法啟動伺服器: %v", err)
	}
}
