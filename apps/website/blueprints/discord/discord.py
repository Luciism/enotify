import os
from urllib.parse import urljoin

from flask import Blueprint, redirect, request, session

from notilib import Database
from helper import (
    build_discord_auth_url,
    enchange_discord_grant,
    fetch_discord_user_dict
)


discord_bp = Blueprint(
    name='discord',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/discord/'
)


callback_redirect_uri = urljoin(os.getenv('base_url'), '/discord/callback')


@discord_bp.route('/discord/authorize')
def authorize():
    # custom `state` url param to persist throughout the auth and callback
    state = request.args.get('state')

    url = build_discord_auth_url(
        client_id=os.getenv('bot_client_id'),
        redirect_uri=callback_redirect_uri,
        state=state
    )
    return redirect(url)


@discord_bp.route('/discord/callback')
async def callback():
    code = request.args.get("code")

    # No code url parameter was provided
    if not code:
        return "Invalid grant!"

    # enchange grant for user access token
    response = await enchange_discord_grant(
        client_id=os.getenv('bot_client_id'),
        client_secret=os.getenv('bot_client_secret'),
        redirect_uri=callback_redirect_uri,
        code=code
    )

    response_data: dict = await response.json()

    # Invalid response
    if response.status != 200:
        return ('Failed to obtain access token', response_data)

    access_token = response_data.get('access_token')

    if access_token is None:
        return f'Failed to obtain access token: {response_data}'

    session['access_token'] = access_token
    return "Successfully logged in!"


@discord_bp.route('/discord/token')
async def token():
    access_token = session.get('access_token')

    user = await fetch_discord_user_dict(access_token, cache=True)
    await Database().cleanup()
    return user or 'no data'
