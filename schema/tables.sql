-- OLD

CREATE TABLE IF NOT EXISTS accounts (
  account_id SERIAL PRIMARY KEY,
  discord_id BIGINT NOT NULL UNIQUE,
  creation_timestamp REAL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP),
  permissions TEXT,  -- comma seperated list of permissions
  blacklisted BOOLEAN DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS gmail_credentials (
  discord_id BIGINT NOT NULL,
  email_address BYTEA NOT NULL,  -- encrypted email address
  credentials BYTEA NOT NULL,  -- encrypted oauth2 user credentials
  valid BOOLEAN DEFAULT TRUE,
  PRIMARY KEY(discord_id, email_address)
);


CREATE TABLE IF NOT EXISTS gmail_latest_email_ids (
  email_address BYTEA NOT NULL UNIQUE,  -- encrypted email address
  latest_email_id TEXT  -- in order to not resend notifications (https://issuetracker.google.com/issues/36759803)
);


-- NEW

CREATE TABLE IF NOT EXISTS accounts (
  account_id SERIAL PRIMARY KEY,
  discord_id BIGINT NOT NULL UNIQUE,
  creation_timestamp REAL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP),
  permissions TEXT[],
  blacklisted BOOLEAN DEFAULT FALSE,
  gmail_email_addresses BYTEA[]
);


CREATE TABLE IF NOT EXISTS gmail_credentials (
  email_address BYTEA NOT NULL,  -- encrypted email address
  credentials BYTEA,  -- encrypted oauth2 user credentials
  valid BOOLEAN DEFAULT TRUE,
  latest_email_id TEXT  -- in order to not resend notification (https://issuetracker.google.com/issues/36759803)
);
