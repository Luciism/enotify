import logging
import os
from urllib.parse import urljoin
from uuid import uuid4

from quart import Blueprint, redirect, request, session

from helper import (
    build_discord_auth_url,
    login_user,
)


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')

discord_bp = Blueprint(
    name='discord',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/'
)

callback_redirect_uri = urljoin(os.getenv('base_url'), '/discord/callback')


@discord_bp.route('/discord/authorize')
async def authorize():
    state = uuid4().hex
    session['csrf_token'] = state

    url = build_discord_auth_url(
        client_id=os.getenv('bot_client_id'),
        redirect_uri=callback_redirect_uri,
        state=state
    )
    return redirect(url)


@discord_bp.route('/discord/callback')
async def callback():
    state = request.args.get("state")

    if state != session.get('csrf_token'):
        return "CSRF token does not match!"

    code = request.args.get("code")
    if not code:
        # No code url parameter was provided
        return "Invalid code!"

    return await login_user(code, callback_redirect_uri)
