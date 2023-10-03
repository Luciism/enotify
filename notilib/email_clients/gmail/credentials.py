import os
import json

from aiogoogle.auth.creds import ClientCreds, UserCreds
from cryptography.fernet import Fernet

from ...database import Database


db = Database()

client_creds = ClientCreds(
    client_id=os.getenv('gcloud_client_id'),
    client_secret=os.getenv('gcloud_client_secret'),
    scopes=[
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email'
    ],
    redirect_uri='http://localhost:5000/gmail/callback'
)

fernet = Fernet(os.getenv('credentials_encryption_key'))


def encrypt_credentials(credentials: dict) -> bytes:
    """
    Encrypts credentials using the `credentials_encryption_key`
    environment variable with `cryptography.fernet` encryption.
    :param credentials: the credentials json to encrypt
    """
    creds_str = json.dumps(credentials)

    return fernet.encrypt(creds_str.encode())


def decrypt_credentials(credentials: bytes | str) -> dict:
    """
    Decrypts credentials using the `credentials_encryption_key`
    environment variable with `cryptography.fernet` decryption.
    :param credentials: the credentials bytes to decrypt
    """
    creds_str = fernet.decrypt(credentials).decode()

    return json.loads(creds_str)


async def save_user_credentials(
    discord_id: int,
    email_address: str,
    credentials: dict
) -> None:
    """
    Save a user's credentials to the database
    :param discord_id: the discord id of the logged in user to associate the\
        email address and credentials with
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param credentials: the encrypted google oauth credentials
    """
    encrypted_credentials = encrypt_credentials(credentials)

    conn = await db.connect()

    current = await conn.fetchrow(
        'SELECT * FROM gmail_credentials WHERE discord_id = $1 AND email_address = $2',
        discord_id, email_address
    )

    if not current:
        await conn.execute(
            'INSERT INTO gmail_credentials (discord_id, email_address, '
            'credentials) VALUES ($1, $2, $3)',
            discord_id, email_address, encrypted_credentials
        )
    else:
        await conn.execute(
            'UPDATE gmail_credentials SET credentials = $1 '
            'WHERE discord_id = $2 AND email_address = $3',
            encrypted_credentials, discord_id, email_address
        )


async def load_user_credentials(
    discord_id: int,
    email_address: str
) -> UserCreds | None:
    """
    Loads specified user credentials from the database
    :param discord_id: the discord id of the account that the credentials\
        are tied to
    :param email_address: the email address of the account that the credentials\
        are tied to
    """
    conn = await db.connect()

    credentials = await conn.fetchrow(
        'SELECT * FROM gmail_credentials WHERE discord_id = $1 AND email_address = $2',
        discord_id, email_address)

    if not credentials:
        return None

    decrypted_credentials = decrypt_credentials(credentials[2])
    return UserCreds(**decrypted_credentials)
