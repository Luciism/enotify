import os
import json

from aiogoogle.auth.creds import ClientCreds, UserCreds
from asyncpg import Connection
from cryptography.fernet import Fernet

from ...database import ensure_connection


client_creds = ClientCreds(
    client_id=os.getenv('gcloud_client_id'),
    client_secret=os.getenv('gcloud_client_secret'),
    scopes=[
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email'
    ],
    redirect_uri=os.getenv('gcloud_redirect_uri')
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


@ensure_connection
async def __find_user_credentials(
    discord_id: int,
    email_address: str,
    conn: Connection=None
):
    """
    Returns credentials matching discord id and email address from database
    :param discord_id: the discord id of the account that the credentials\
        are tied to
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    # select all rows of credentials bound to the discord user
    all_creds = await conn.fetch(
        'SELECT * FROM gmail_credentials WHERE discord_id = $1', discord_id)

    # because the encryption algorithm fernet uses is not deterministic,
    # we have to loop through the credentials and decrypt each of them in
    # order to see if the match
    for creds in all_creds:
        decrypted_email_addr = fernet.decrypt(creds['email_address']).decode()

        if decrypted_email_addr == email_address:
            return creds
    return None


@ensure_connection
async def save_user_credentials(
    discord_id: int,
    email_address: str,
    credentials: dict,
    conn: Connection=None
) -> None:
    """
    Save a user's credentials to the database
    :param discord_id: the discord id of the logged in user to associate the\
        email address and credentials with
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param credentials: the encrypted google oauth credentials
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    # find any existing record that has the same discord id and email address
    # through interation since the ciphertext is non deterministic
    existing = await __find_user_credentials(discord_id, email_address, conn=conn)

    encrypted_credentials = encrypt_credentials(credentials)

    if existing:
        await conn.execute(
            'UPDATE gmail_credentials SET credentials = $1 '
            'WHERE discord_id = $2 AND email_address = $3',
            encrypted_credentials, discord_id, existing['email_address']
        )
        return

    encrypted_email_addr = fernet.encrypt(email_address.encode())
    await conn.execute(
        'INSERT INTO gmail_credentials (discord_id, email_address, '
        'credentials) VALUES ($1, $2, $3)',
        discord_id, encrypted_email_addr, encrypted_credentials
    )


@ensure_connection
async def load_user_credentials(
    discord_id: int,
    email_address: str,
    conn: Connection=None
) -> UserCreds | None:
    """
    Loads specified user credentials from the database
    :param discord_id: the discord id of the account that the credentials\
        are tied to
    :param email_address: the email address of the account that the credentials\
        are tied to
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    # obtain raw record for respective discord id and email
    creds = await __find_user_credentials(discord_id, email_address, conn=conn)

    if creds:
        # decrypt and return UserCreds object for the credentials
        decrypted_creds = decrypt_credentials(creds['credentials'])
        return UserCreds(**decrypted_creds)

    return None
