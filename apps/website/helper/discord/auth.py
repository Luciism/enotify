import os
import urllib.parse
from datetime import datetime

from aiohttp import ClientSession, ClientResponse
from aiohttp_client_cache import CachedSession, SQLiteBackend
from quart import session

from notilib import create_account
from .info import get_discord_avatar
from ..exceptions import InvalidDiscordAccessTokenError, UserNotLoggedInError
from ..utils import response_msg, ResponseMsg


# main requests cache db
cache_backend = SQLiteBackend(
    cache_name='.cache/cache', expire_after=150, include_headers=True)


class DiscordUserCreds:
    def __init__(self, creds_data: dict) -> None:
        self.token_type: str = creds_data.get('token_type')
        self.access_token: str = creds_data.get('access_token')
        self.expires_in: int = creds_data.get('expires_in')
        self.refresh_token: str = creds_data.get('refresh_token')
        self.scope: str = creds_data.get('scope', '')

        self.scopes: list = self.scope.split(' ')


        expires_at = int(datetime.utcnow().timestamp()) + self.expires_in
        self.expires_at = expires_at - 5 # remove 5 seconds to account for request time


class DiscordUser:
    def __init__(self, discord_info: dict) -> None:
        """
        Discord user information wrapper class
        :param discord_info: json response of `https://discord.com/api/users/@me`
        """
        self.accent_color: int = discord_info.get('accent_color')

        self.avatar_url = get_discord_avatar(discord_info)
        self.avatar: str = discord_info.get('avatar')
        self.avatar_decoration_data: str | None =\
            discord_info.get('avatar_decoration_data')

        self.banner: str | None = discord_info.get('banner')
        self.banner_color: str = discord_info.get('banner_color')

        self.discriminator: int = _int_or_none(discord_info.get('discriminator'))

        self.global_name: str = discord_info.get('global_name')
        self.username: str = discord_info.get('username')
        self.id: int = _int_or_none(discord_info.get('id'))

        self.mfa_enabled: bool = discord_info.get('mfa_enabled')
        self.premium_type: int = discord_info.get('premium_type')

        self.locale: str = discord_info.get('locale')
        self.flags: int = discord_info.get('flags')
        self.public_flags: int = discord_info.get('public_flags')


    def __getitem__(self, key: str):
        # key is a string, is not a private / dunder attr, and class has attr
        if not isinstance(key, str) or key.startswith('__') or not hasattr(self, key):
            raise KeyError(key)

        return self.__getattribute__(key)


    def __repr__(self) -> str:
        return str(self.__dict__)


async def _make_discord_token_endpoint_request(data: dict) -> ClientResponse:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with ClientSession() as session:
        response = await session.post(
            "https://discord.com/api/oauth2/token",
            headers=headers, data=data, timeout=10
        )
        return response


def _int_or_none(value: str) -> int | None:
    """Returns `None` if a `TypeError` is raised otherwise `int(value)`"""
    try:
        return int(value)
    except TypeError:
        return None


async def _fetch_discord_user_req(
    access_token: str,
    session: ClientSession | CachedSession
):
    """Makes actual request with given session"""
    response = await session.get(
        url='https://discord.com/api/users/@me',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10
    )
    return response


async def _fetch_discord_user(access_token: str, cache: bool=False):
    """Determines session and then makes request"""
    if not cache:
        # use regular `aiohttp.ClientSession()`
        async with ClientSession() as session:
            return await _fetch_discord_user_req(access_token, session)

    # use `aiohttp_client_cache.CachedSession()` with custom sqlite3 backend
    async with CachedSession(
        cache=SQLiteBackend(
            cache_name='.cache/cache', expire_after=150, include_headers=True)
    ) as session:
        return await _fetch_discord_user_req(access_token, session)


class DiscordOauthClient:
    def __init__(
        self,
        redirect_uri: str,
        client_id: int=None,
        client_secret: str=None,
    ) -> None:
        self.client_id = client_id or os.getenv('bot_client_id')
        self.client_secret = client_secret or os.getenv('bot_client_secret')
        self.redirect_uri = redirect_uri


    def build_discord_auth_url(
        self,
        state: str,
        scopes: list=['identify'],
        response_type: str='code'
    ) -> str:
        """
        Builds a discord oauth2 url using the provided information
        :param state: randomly generated csrf token to validate the request origin
        :param scopes: a list of discord scopes
        :param response_type: the response type for receiving the grant code
        """
        # join scopes into url encoded string
        scopes = urllib.parse.quote(' '.join(scopes))

        # parse redirect uri into url encoded string
        redirect_uri = urllib.parse.quote(self.redirect_uri, safe='')

        url = (
            f'https://discord.com/api/oauth2/authorize?client_id={self.client_id}'
            f'&redirect_uri={redirect_uri}&response_type={response_type}'
            f'&scope={scopes}&state={state}'
        )

        return url


    async def __enchange_discord_grant_code(
        self,
        code: str
    ) -> ClientResponse:
        """
        Exchanges discord oauth2 grant code for access token credentials
        :param code: the discord oauth2 grant code returned in the callback
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "scope": "identify"
        }

        # Exchange the authorization code for an access token
        return await _make_discord_token_endpoint_request(data)


    async def login_user(
        self,
        code: str,
        required_scopes: list[str]=['identify']
    ) -> ResponseMsg:
        """
        TODO: setup proper responses with pages\n
        Logs a user in to the website using discord oauth
        :param code: the discord grant code present in the `code` parameter\
            of the callback url
        :param required_scopes: the scopes that the user is required to grant in\
            order to login
        """
        # enchange grant for user access token
        response = await self.__enchange_discord_grant_code(
            code=code
        )

        return await self.set_discord_user_creds(response, required_scopes)


    async def refresh_discord_access_token(
        self,
        refresh_token: str
    ) -> ClientResponse:
        """
        Refreshes a discord access token credential
        :param refresh_token: the refresh token to use in order to refresh\
            the access token
        """
        # Exchange the authorization code for an access token
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        return await _make_discord_token_endpoint_request(data)


    async def authenticate_user(
        self,
        required_scopes: list[str]=['identify']
    ) -> DiscordUser:
        """
        Validates that the user that is currently being handled
        is logged in (with discord oauth)
        :param required_scopes: the scopes the user is required to have granted\
            in order for the login to succeed
        """
        # fetch discord user using access token stored in user's session cookie
        discord_credentials: dict = session.get('discord_credentials')
        if discord_credentials is None:
            raise UserNotLoggedInError

        expires_at: int = discord_credentials.get('expires_at')

        # access token has not expired
        if not datetime.utcnow().timestamp() >= expires_at:
            refresh_token: str = discord_credentials.get('refresh_token')
            access_token: str = discord_credentials.get('access_token')

            user = await DiscordOauthClient.fetch_discord_user(access_token, cache=True)

            # everything is valid
            if user is not None:
                return user

        # token is outdated or invalid, attempt to
        # refresh and update discord credentials in session cookie
        response = await self.refresh_discord_access_token(refresh_token)
        await DiscordOauthClient.set_discord_user_creds(response, required_scopes)

        # refetch user using new access token
        new_access_token = (await response.json()).get('access_token')

        user = await DiscordOauthClient.fetch_discord_user(
            access_token=new_access_token, cache=True)

        # user is still not valid, raise error
        if user is None:
            raise InvalidDiscordAccessTokenError

        return user


    @staticmethod
    async def set_discord_user_creds(
        response: ClientResponse,
        required_scopes: list[str]=['identify']
    ) -> ResponseMsg:
        """
        Sets the discord credentials in the session cookie if everything
        is valid
        :param response: the raw discord `ClientResponse` object from the\
            `/api/oauth2/token` endpoint
        :param required_scopes: the scopes the user is required to have granted\
            in order for the login to succeed
        """
        if response.status != 200:
            return response_msg('discord_oauth_error')

        response_data: dict = await response.json()
        creds = DiscordUserCreds(response_data)

        # ensure response data is intact
        if not (
            isinstance(creds.access_token, str) and
            isinstance(creds.refresh_token, str) and
            isinstance(creds.expires_in, int)
        ):
            return response_msg('malformed_response_data')

        # ensure required scopes are met
        for scope in required_scopes:
            if not scope in creds.scopes:
                return response_msg('invalid_scopes')

        # store credentials in session cookie
        session['discord_credentials'] = creds.__dict__

        return response_msg('discord_oauth_login_success')


    @staticmethod
    async def fetch_discord_user_dict(
        access_token: str,
        cache: bool=False
    ) -> dict | None:
        """
        Fetches a user's discord information using their access token as a dict
        :param access_token: the access token of the user to get the information of
        :param cache: whether or not to use the cache system
        """
        if access_token is None:
            return None

        response = await _fetch_discord_user(access_token, cache=cache)

        # Invalid response
        if response.status != 200:
            return None

        # return json response as a dict
        discord_info: dict = await response.json()

        # return `None` if account is still not valid
        if discord_info.get('id') is None:
            return None

        # create account if it doesn't exist
        await create_account(int(discord_info.get('id')))
        return discord_info


    @staticmethod
    async def fetch_discord_user(
        access_token: str,
        cache: bool=False
    ) -> DiscordUser | None:
        """
        Fetches a user's discord information using their access token
        :param access_token: the access token of the user to get the information of
        :param cache: whether or not to use the cache system
        """
        discord_info = await DiscordOauthClient.fetch_discord_user_dict(
            access_token, cache=cache)

        # account does not exist
        if not discord_info or not discord_info.get('id'):
            return None

        # convert user information dict to custom DiscordUser class
        return DiscordUser(discord_info)


discord_auth_client = DiscordOauthClient(
    redirect_uri=urllib.parse.urljoin(os.getenv('base_url'), '/discord/callback')
)
