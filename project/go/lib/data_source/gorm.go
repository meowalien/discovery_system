package data_source

import (
	"context"
	"go-root/lib/errs"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func NewGormDB(ctx context.Context, dsn string) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, errs.New(err)
	}
	// ping the database to check if it's reachable
	sqlDB, err := db.DB()
	if err != nil {
		return nil, errs.New(err)
	}
	if e := sqlDB.PingContext(ctx); e != nil {
		return nil, errs.New(e)
	}

	return db, nil
}
