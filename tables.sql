CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    creation_timestamp REAL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP),
    permissions TEXT,  -- comma seperated list of permissions
    blacklisted BOOLEAN DEFAULT FALSE
);


CREATE TABLE gmail_credentials (
    discord_id BIGINT NOT NULL,
    email_address BYTEA NOT NULL,  -- encrypted email address
    credentials BYTEA NOT NULL,  -- encrypted oauth2 user credentials
    valid BOOLEAN DEFAULT TRUE,
    PRIMARY KEY(discord_id, email_address)
);


CREATE TABLE gmail_latest_email_ids (
    email_address BYTEA NOT NULL UNIQUE,  -- encrypted email address
    latest_email_id TEXT  -- in order to not resend notifications (https://issuetracker.google.com/issues/36759803)
);

-- example usage
INSERT INTO gmail_latest_email_ids (email_address, lastest_email_id)
VALUES (pgp_sym_encrypt('example@gmail.com', 'encryption_key'), 'abc123');

SELECT pgp_sym_decrypt(email_address, 'encryption_key'), lastest_email_id
FROM gmail_latest_email_ids WHERE pgp_sym_decrypt(email_address, 'encryption_key') = 'example@gmail.com';
