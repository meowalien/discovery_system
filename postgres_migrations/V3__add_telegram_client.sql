CREATE TABLE telegram_reader.telegram_client
(
    user_id VARCHAR(36),
    session_id UUID NOT NULL,
    FOREIGN KEY (user_id) REFERENCES keycloak.user_entity (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    PRIMARY KEY (user_id, session_id)
);