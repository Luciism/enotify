import os
import json
import logging

from aiogoogle import HTTPError
from aiogoogle.auth import Oauth2Manager
from aiogoogle.auth.creds import ClientCreds, UserCreds
from asyncpg import Connection

from ...exceptions import InvalidRefreshTokenError
from ...database import ensure_connection
from ...functions import config


logger = logging.getLogger(__name__)

client_creds = ClientCreds(
    client_id=os.getenv('gcloud_client_id'),
    client_secret=os.getenv('gcloud_client_secret'),
    scopes=config('global.gmail.scopes'),
    redirect_uri=os.getenv('gcloud_redirect_uri')
)
oauth2 = Oauth2Manager(client_creds=client_creds)


@ensure_connection
async def __find_user_credentials(
    email_address: str,
    conn: Connection=None
) -> dict | None:
    """
    Returns credentials corresponding to a specific email address from database
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    credentials = await conn.fetchval(
        'SELECT pgp_sym_decrypt(credentials, $2) FROM gmail_credentials '
        'WHERE pgp_sym_decrypt(email_address, $2) = $1',
        email_address, os.getenv('database_encryption_key')
    )

    if credentials:
        return json.loads(credentials)
    return None


@ensure_connection
async def set_credentials_validity(
    email_address: str,
    valid: bool=False,
    conn: Connection=None
) -> bool:
    """
    Sets `valid` column of stored credentials to `True` or `False`
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param valid: the value to set the credential validity to (`True`, `False`)
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)

    :return: whether the credentials existed in the database and were updated
    """
    current = await __find_user_credentials(email_address, conn=conn)
    if not current:
        return False

    await conn.execute(
        'UPDATE gmail_credentials SET valid = $1 '
        'WHERE pgp_sym_decrypt(email_address, $3) = $2',
        valid, email_address, os.getenv('database_encryption_key')
    )
    return True


@ensure_connection
async def refresh_user_credentials(
    email_address: str,
    user_creds: UserCreds,
    conn: Connection=None
) -> UserCreds:
    """
    Refreshes user credentials if they are expired
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param user_creds: the credentials to refresh if expired
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    # refresh credentials if they are expired
    try:
        did_refresh, user_creds = await oauth2.refresh(user_creds=user_creds)
    except HTTPError as exc:
        # raise invalid refresh error if error http error is due to an invalid grant
        if exc.res.json['error'] == 'invalid_grant':
            await set_credentials_validity(email_address, valid=False, conn=conn)
            raise InvalidRefreshTokenError(
                'Invalid google account refresh token credential!') from exc
        # otherwise reraise
        raise

    if did_refresh:
        logger.debug('Refreshed Oauth2 user credentials')

        # update the credentials in the database to reflect the refreshed credentials
        await save_user_credentials(email_address, user_creds, conn=conn)

    return user_creds


@ensure_connection
async def save_user_credentials(
    email_address: str,
    user_creds: UserCreds,
    conn: Connection=None
) -> None:
    """
    Save a user's credentials to the database
    :param email_address: the email address for the google account that the\
        credentials are tied to
    :param credentials: the encrypted google oauth credentials
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    # find any existing record that has the same discord id and email address
    # through interation since the ciphertext is non deterministic
    existing = await __find_user_credentials(email_address, conn=conn)

    credentials = json.dumps(user_creds)

    if existing:
        await conn.execute(
            'UPDATE gmail_credentials SET credentials = pgp_sym_encrypt($1, $3) '
            'WHERE pgp_sym_decrypt(email_address, $3) = $2',
            credentials, email_address, os.getenv('database_encryption_key'),
        )
        return

    await conn.execute(
        'INSERT INTO gmail_credentials (email_address, credentials) '
        'VALUES (pgp_sym_encrypt($1, $3), pgp_sym_encrypt($2, $3))',
        email_address, credentials, os.getenv('database_encryption_key')
    )


@ensure_connection
async def load_user_credentials(
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
        one will be acquired automatically (must be passed as a keyword argument)
    """
    # obtain raw record for respective discord id and email
    creds = await __find_user_credentials(email_address, conn=conn)
    if creds is None:
        return None

    user_creds = UserCreds(**creds)
    user_creds = await refresh_user_credentials(
        email_address, user_creds, conn=conn)

    return user_creds


@ensure_connection
async def load_all_user_credentials(
    conn: Connection=None
) -> list[UserCreds]:
    """
    Returns list of all valid user credentials in the database
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    all_creds: list[UserCreds] = []

    # select all valid user credentials
    rows = await conn.fetch(
        'SELECT pgp_sym_decrypt(email_address, $1) AS email_address, '
        'pgp_sym_decrypt(credentials, $1) AS credentials '
        'FROM gmail_credentials WHERE valid = true',
        os.getenv('database_encryption_key')
    )

    # iterate over all credentials and validate them
    for row in rows:
        credentials: str = row['credentials']
        email_address: str = row['email_address']

        if credentials is None:
            continue

        # load credentials
        user_creds = UserCreds(**json.loads(credentials))

        # attempt to refresh the credentials, but if they are invalid, set the
        # credentials validity to false in the database and continue.
        try:
            user_creds = await refresh_user_credentials(
                email_address=email_address, user_creds=user_creds, conn=conn)
        except InvalidRefreshTokenError:
            await set_credentials_validity(
                email_address=email_address, valid=False, conn=conn)
            continue

        # add valid credentials to current batch
        all_creds.append(user_creds)

    return all_creds
