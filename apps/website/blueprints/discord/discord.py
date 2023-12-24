import logging
from uuid import uuid4

from quart import Blueprint, redirect, request, session

from helper import next_or_fallback, discord_auth_client


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')

discord_bp = Blueprint(
    name='discord',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/'
)


@discord_bp.route('/discord/authorize')
async def authorize():
    if request.args.get('next'):
        session['next_url'] = request.args.get('next')

    state = uuid4().hex
    session['csrf_token'] = state

    url = discord_auth_client.build_discord_auth_url(state=state)
    return redirect(url)


@discord_bp.route('/discord/callback')
async def callback():
    state = request.args.get("state")
    if state != session.get('csrf_token'):
        return redirect('/error/csrf_token_mismatch')

    code = request.args.get("code")
    if not code:
        # No code url query parameter was provided
        return redirect('/error/code_grant_invalid')

    res = await discord_auth_client.login_user(code)

    # something probably went wrong, returning error page
    if res is not None:
        return res

    return next_or_fallback()  # redirect user to home or next page

