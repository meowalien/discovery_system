ALTER TABLE telegram_reader.sessions
    ADD COLUMN api_id BIGINT,
    ADD COLUMN api_hash TEXT
;