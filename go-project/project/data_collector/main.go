package main

import (
	"core"
	"fmt"
	"google.golang.org/grpc/credentials/insecure"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"

	// Qdrant 客戶端
	"github.com/qdrant/go-client/qdrant"
	"google.golang.org/grpc"
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

	version := core.GetConfig().Version
	fmt.Println("version: ", version)

	// 初始化 Logrus
	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})
	logrus.SetLevel(logrus.DebugLevel)
	qdrantHost := viper.GetString("qdrant.host")
	qdrantPort := viper.GetInt("qdrant.port")

	// 嘗試連線 Qdrant（如果有需要的話）
	// 這邊只示範如何建立連線
	address := fmt.Sprintf("%s:%d", qdrantHost, qdrantPort)
	conn, err := grpc.NewClient(address, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		logrus.Errorf("連線 Qdrant 失敗: %v", err)
	} else {
		// 初始化客戶端
		qdrantClient := qdrant.NewQdrantClient(conn)
		logrus.Infof("成功連線 Qdrant，位於 %s", address)

		// 範例：可以在這裡使用 qdrantClient 執行各種操作
		// e.g. qdrantClient.ListCollections(...)
		_ = qdrantClient
	}

	// 建立 Gin 引擎
	r := gin.Default()

	// 註冊 /version 路徑
	r.GET("/version", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"version": version,
		})
	})

	// 啟動 Server
	logrus.Infof("啟動 HTTP 伺服器，http://localhost:8080/ ...")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("無法啟動伺服器: %v", err)
	}
}
