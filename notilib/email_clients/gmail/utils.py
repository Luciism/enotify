import logging
import warnings
import os

from aiohttp import ClientSession
from aiogoogle import Aiogoogle, HTTPError
from aiogoogle.auth.creds import UserCreds
from aiogoogle.utils import _dict
from asyncpg import Connection

from .credentials import client_creds, oauth2
from ...database import ensure_connection
from ...exceptions import InvalidResetTokenError


logger = logging.getLogger(__name__)
warnings.simplefilter('ignore')


class UserInfo(_dict):
    def __init__(self, user_info: dict):
        self.error = user_info.get('error')
        self.id: int = user_info.get('id')
        self.email: str = user_info.get('email')
        self.verified_email: bool = user_info.get('verified_email')
        self.picture: str = user_info.get('picture')


async def get_user_info(user_creds: UserCreds) -> dict | UserInfo:
    """
    Returns google account user information from the
    `https://www.googleapis.com/oauth2/v2/userinfo` endpoint.

    Example output:
    ```py
    {
        'id': '106211250550335513632',
        'email': 'example@gmail.com',
        'verified_email': True,
        'picture': 'https://lh3.googleusercontent.com/a-/abc123'
    }
    ```
    :param user_creds: the google auth credentials of the user\
        to fetch the information of
    """
    # Refreshes credentials if they are expired, otherwise just returns them as is
    try:
        refreshed, user_creds = await oauth2.refresh(user_creds=user_creds)
    except HTTPError as exc:
        raise InvalidResetTokenError(
            'Invalid google account refresh token credential!') from exc

    if refreshed:
        logger.info('User credentials were refreshed!')

    async with ClientSession() as session:
        headers = {'Authorization': f'Bearer {user_creds.access_token}'}

        # send get request to userinfo endpoint with the user's access token as
        # the Authorization header
        res = await session.get(
            'https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)

        user_info: dict = await res.json()

    # return the user info as a custom dict type
    return UserInfo(user_info)


@ensure_connection
async def email_address_to_discord_ids(
    email_address: str,
    conn: Connection=None
) -> list[int]:
    """
    Returns a list of discord ids that have a certain email tied to them
    :param email_address: the email address to find the respective discord ids of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    rows = await conn.fetch(
        'SELECT discord_id FROM gmail_credentials '
        'WHERE pgp_sym_decrypt(email_address, $2) = $1',
        email_address, os.getenv('database_encryption_key'))

    return [row['discord_id'] for row in rows]
