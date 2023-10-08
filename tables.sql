CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    creation_timestamp REAL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP),
    permissions TEXT,
    blacklisted INTEGER DEFAULT 0 CHECK (blacklisted = 0 OR blacklisted = 1)
);


CREATE TABLE gmail_credentials (
    discord_id BIGINT NOT NULL,
    email_address BYTEA NOT NULL,
    credentials BYTEA NOT NULL,
    PRIMARY KEY(discord_id, email_address)
);
