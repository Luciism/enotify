import os
import json
import logging

from aiogoogle import HTTPError
from aiogoogle.models import Request
from aiogoogle.auth import Oauth2Manager
from aiogoogle.auth.creds import ClientCreds, UserCreds
from asyncpg import Connection

from ...exceptions import InvalidResetTokenError
from ...database import ensure_connection


logger = logging.getLogger(__name__)

client_creds = ClientCreds(
    client_id=os.getenv('gcloud_client_id'),
    client_secret=os.getenv('gcloud_client_secret'),
    scopes=[
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email'
    ],
    redirect_uri=os.getenv('gcloud_redirect_uri')
)
oauth2 = Oauth2Manager(client_creds=client_creds)


@ensure_connection
async def __find_user_credentials(
    discord_id: int,
    email_address: str,
    conn: Connection=None
) -> dict | None:
    """
    Returns credentials matching discord id and email address from database
    :param discord_id: the discord id of the account that the credentials\
        are tied to
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    credentials = await conn.fetchval(
        'SELECT pgp_sym_decrypt(credentials, $3) FROM gmail_credentials '
        'WHERE discord_id = $1 AND pgp_sym_decrypt(email_address, $3) = $2',
        discord_id, email_address, os.getenv('database_encryption_key'))

    if credentials:
        return json.loads(credentials)
    return None


@ensure_connection
async def set_credentials_validity(
    discord_id: int,
    email_address: str,
    valid: bool=False,
    conn: Connection=None
) -> bool:
    """
    Sets `valid` column of stored credentials to `True` or `False`
    :param discord_id: the discord id of the account that the credentials\
        are tied to
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param valid: the value to set the credential validity to (`True`, `False`)
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    :return: whether the credentials existed in the database and were updated
    """
    current = await __find_user_credentials(discord_id, email_address, conn=conn)
    if not current:
        return False

    await conn.execute(
        'UPDATE gmail_credentials SET valid = $1 '
        'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $4) = $3',
        valid, discord_id, email_address, os.getenv('database_encryption_key')
    )
    return True


@ensure_connection
async def refresh_user_credentials(
    discord_id: int,
    email_address: str,
    user_creds: UserCreds,
    conn: Connection=None
) -> UserCreds:
    """
    Refreshes user credentials if they are expired
    :param discord_id: the discord id of the account that the credentials\
        are tied to
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param user_creds: the credentials to refresh if expired
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    # refresh credentials if they are expired
    try:
        did_refresh, user_creds = await oauth2.refresh(user_creds=user_creds)
    except HTTPError as exc:
        res: Request = exc.res
        if res.json['error'] == 'invalid_grant':
            await set_credentials_validity(
                discord_id, email_address, valid=False, conn=conn)
            raise InvalidResetTokenError(
                'Invalid google account refresh token credential!') from exc
        raise

    if did_refresh:
        logger.debug('Refreshed Oauth2 user credentials')

        # update the credentials in the database to reflect the refreshed credentials
        await save_user_credentials(discord_id, email_address, user_creds, conn=conn)

    return user_creds


@ensure_connection
async def save_user_credentials(
    discord_id: int,
    email_address: str,
    user_creds: UserCreds,
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

    credentials = json.dumps(user_creds)

    if existing:
        await conn.execute(
            'UPDATE gmail_credentials SET credentials = pgp_sym_encrypt($1, $4) '
            'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $4) = $3',
            credentials, discord_id, email_address, os.getenv('database_encryption_key'),
        )
        return

    await conn.execute(
        'INSERT INTO gmail_credentials (discord_id, email_address, credentials) '
        'VALUES ($1, pgp_sym_encrypt($2, $4), pgp_sym_encrypt($3, $4))',
        discord_id, email_address, credentials, os.getenv('database_encryption_key')
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
    if creds is None:
        return None

    user_creds = UserCreds(**creds)
    user_creds = await refresh_user_credentials(
        discord_id, email_address, user_creds, conn=conn)

    return user_creds
