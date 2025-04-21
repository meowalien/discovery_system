package dal

import "github.com/google/uuid"

// TelegramClient maps to the telegram_client table.
type TelegramClient struct {
	UserID    string    `gorm:"column:user_id;type:varchar(36);not null;primaryKey"`
	SessionID uuid.UUID `gorm:"column:session_id;type:uuid;not null;primaryKey"`
}
