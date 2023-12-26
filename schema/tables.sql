CREATE TABLE IF NOT EXISTS accounts (
  account_id SERIAL PRIMARY KEY,
  discord_id BIGINT NOT NULL UNIQUE,
  creation_timestamp REAL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP),
  permissions TEXT[],
  blacklisted BOOLEAN DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS gmail_credentials (
  email_address BYTEA NOT NULL,  -- encrypted email address
  credentials BYTEA,  -- encrypted oauth2 user credentials
  valid BOOLEAN DEFAULT TRUE,
  latest_email_id TEXT  -- in order to not resend notification (https://issuetracker.google.com/issues/36759803)
);

CREATE TABLE IF NOT EXISTS email_notification_filters (
  discord_id BIGINT NOT NULL,
  email_address BYTEA NOT NULL,
  webmail_service TEXT NOT NULL,
  sender_whitelist_enabled BOOL DEFAULT FALSE,
  whitelisted_senders BYTEA[],
  blacklisted_senders BYTEA[],
  PRIMARY KEY(discord_id, email_address)
);
