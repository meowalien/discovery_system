--     api_id: Mapped[int] = mapped_column(Integer)
--     api_hash: Mapped[str] = mapped_column(Text)
ALTER TABLE telegram_reader.sessions
    ADD COLUMN api_id BIGINT,
    ADD COLUMN api_hash TEXT
;