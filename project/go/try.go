package main

import (
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	// 你的連線字串
	dsn := "postgresql://postgres:postgres@postgres-headless.default:5432/discovery_system"

	// 開啟 GORM 連線
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("❌ 無法連接資料庫: %v", err)
	}

	// 取得底層 *sql.DB 以進行 Ping 或其他設定
	sqlDB, err := db.DB()
	if err != nil {
		log.Fatalf("❌ 取得底層資料庫物件失敗: %v", err)
	}

	// 確認連線存活
	if err := sqlDB.Ping(); err != nil {
		log.Fatalf("❌ 資料庫 Ping 失敗: %v", err)
	}

	log.Println("✅ 成功連接到 PostgreSQL！")
	// 如果有 model，需要自動遷移可以這樣呼叫：
	// type User struct {
	//   ID    uint
	//   Name  string
	//   Email string
	// }
	// if err := db.AutoMigrate(&User{}); err != nil {
	//   log.Fatalf("❌ 自動遷移失敗: %v", err)
	// }
}
