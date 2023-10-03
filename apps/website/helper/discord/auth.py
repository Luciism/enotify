import urllib.parse

from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession, SQLiteBackend

from notilib import create_account


# main requests cache db
cache_backend = SQLiteBackend(
    cache_name='.cache/cache', expire_after=150)


def build_discord_auth_url(
    client_id: int,
    redirect_uri: str,
    scopes: list=['identify'],
    response_type: str='code',
    state: str | None=None
):
    """
    Builds a discord oauth2 url using the provided information
    :param client_id: the client id of the bot to authenticate with
    :param redirect_uri: the redirect uri to go to once the user has authenticated
    :param scopes: a list of discord scopes
    :param state: any extra value that will be passed back with the redirect uri
    :param response_type: the response type for receiving the grant code
    """
    # join scopes into url encoded string
    scopes = urllib.parse.quote(' '.join(scopes))

    # parse redirect uri into url encoded string
    redirect_uri = urllib.parse.quote(redirect_uri, safe='')

    url = (
        f'https://discord.com/api/oauth2/authorize?client_id={client_id}'
        f'&redirect_uri={redirect_uri}&response_type={response_type}&scope={scopes}'
    )

    # add state param
    if state:
        url += f'&state={state}'

    return url


async def enchange_discord_grant(
    client_id: int,
    client_secret: str,
    code: str,
    redirect_uri: str
) :
    # Exchange the authorization code for an access token
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": "identify"
    }

    async with ClientSession() as session:
        response = await session.post(
            "https://discord.com/api/oauth2/token",
            headers=headers, data=data, timeout=10
        )
        return response


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


def _safe_int(value: str) -> int | None:
    """Returns `None` if a `TypeError` is raised otherwise `int(value)`"""
    try:
        return int(value)
    except TypeError:
        return None


class DiscordUser:
    def __init__(self, discord_info: dict) -> None:
        """
        Discord user information wrapper class
        :param discord_info: json response of `https://discord.com/api/users/@me`
        """
        self.accent_color: int = discord_info.get('accent_color')

        self.avatar: str = discord_info.get('avatar')
        self.avatar_decoration_data: str | None =\
            discord_info.get('avatar_decoration_data')

        self.banner: str | None = discord_info.get('banner')
        self.banner_color: str = discord_info.get('banner_color')

        self.discriminator: int = _safe_int(discord_info.get('discriminator'))

        self.global_name: str = discord_info.get('global_name')
        self.username: str = discord_info.get('username')
        self.id: int = _safe_int(discord_info.get('id'))

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


async def _fetch_discord_user(access_token: str, cache: bool=False):
    """Determines session and then makes request"""
    if not cache:
        # use regular `aiohttp.ClientSession()`
        async with ClientSession() as session:
            return await _fetch_discord_user_req(access_token, session)

    # use `aiohttp_client_cache.CachedSession()` with custom sqlite3 backend
    async with CachedSession(cache=cache_backend) as session:
        return await _fetch_discord_user_req(access_token, session)


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
    # close conn after since flask uses a different event loop for each request
    await create_account(int(discord_info.get('id')))
    return discord_info


async def fetch_discord_user(
    access_token: str,
    cache: bool=False
) -> DiscordUser | None:
    """
    Fetches a user's discord information using their access token
    :param access_token: the access token of the user to get the information of
    :param cache: whether or not to use the cache system
    """
    discord_info = await fetch_discord_user_dict(access_token, cache)

    # account does not exist
    if not discord_info or not discord_info.get('id'):
        return None

    # convert user information dict to custom DiscordUser class
    return DiscordUser(discord_info)
