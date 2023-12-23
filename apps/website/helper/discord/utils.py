from notilib import MISSING
from .auth import DiscordUser, discord_auth_client


def page_user_context_data(user: DiscordUser | None) -> dict | None:
    """
    Returns the relevant data for a user that should be served alongside
    any webpage
    :param user: the discord user data to return the filtered data of
    """
    if user is None:
        return None

    return {
        'avatar_url': user.avatar_url
    }


async def default_page_context_data(user: DiscordUser | None=MISSING) -> dict:
    """
    Returns the default context data for any page
    :param user: prefetched discord user object to use the data of
    """
    if user is MISSING:
        user = await discord_auth_client.authenticate_user_login_optional()

    return {
        'user': page_user_context_data(user)
    }
