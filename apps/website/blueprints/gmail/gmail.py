import os
import logging
from urllib.parse import urljoin
from uuid import uuid4

import jwt
from aiogoogle import HTTPError
from aiogoogle.auth import UserCreds
from quart import (
    Blueprint,
    redirect,
    request,
    session
)

from notilib import Database
from notilib.email_clients import gmail
from helper import (
    DiscordUser,
    gmail_received_notify_user,
    next_or_fallback,
    discord_auth_client,
    root_logger
)


logger = logging.getLogger(__name__)

jwt_client = jwt.PyJWKClient('https://www.googleapis.com/oauth2/v2/certs')
oauth2 = gmail.oauth2

jwt_audience = urljoin(
    os.getenv('base_url'),
    f'/gmail/push?token={os.getenv("gmail_push_route_token")}'  # route with token
)


gmail_bp = Blueprint(
    name='gmail',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/'
)

@gmail_bp.before_app_serving
def before_app_serving():
    root_logger.info(f'Blueprint registered: {__name__}')


def user_creds_arent_intact(user_creds: UserCreds) -> bool:
    return not (
        isinstance(user_creds.get('access_token'), str) and
        isinstance(user_creds.get('refresh_token'), str) and
        isinstance(user_creds.get('id_token'), str) and
        isinstance(user_creds.get('expires_in'), int)
    )


async def add_user_creds(
    user: DiscordUser,
    user_info: gmail.UserInfo,
    user_creds: UserCreds
) -> None:
    pool = await Database().connect()

    async with pool.acquire() as conn:
        await gmail.GmailEmailAddress(
            user.id, user_info.email).add_email_address(conn=conn)
        await gmail.save_user_credentials(user_info.email, user_creds, conn=conn)
        await gmail.set_previous_email_ids(user_info.email, conn=conn)

        await gmail.set_credentials_validity(user_info.email, valid=True, conn=conn)

    await Database().cleanup()


@gmail_bp.route('/gmail/authorize')
async def authorize():
    if request.args.get('next'):
        session['next_url'] = request.args.get('next')

    state = uuid4().hex
    session['csrf_token'] = state

    auth_url = oauth2.authorization_url(
        client_creds=gmail.client_creds,
        state=state,
        access_type='offline',
        prompt='consent'
    )
    return redirect(auth_url)


@gmail_bp.route('/gmail/callback/')
async def callback():
    # make sure the user is logged in
    user = await discord_auth_client.authenticate_user()

    state = request.args.get('state')
    if state != session.get('csrf_token'):
        return redirect('/error/csrf_token_mismatch')

    # On error, show user error message and log error data
    if request.args.get('error'):
        logger.info('(`/gmail/callback` error) ' + str({
            'error': request.args.get('error'),
            'error_description': request.args.get('error_description')
        }))
        return redirect('/error/auth_error')

    if not request.args.get('code'):
        # Should either receive a code or an error
        return redirect('/error/code_grant_invalid')

    # Exchange code for the access and refresh token
    try:
        # build user creds from code query parameter
        user_creds: UserCreds = await oauth2.build_user_creds(
            grant=request.args.get('code'),
            client_creds=gmail.client_creds
        )
    except HTTPError:
        return redirect('/error/code_grant_invalid')

    # make sure required scopes have been authorized
    for scope in gmail.client_creds.scopes:
        if scope not in user_creds.scopes:
            return redirect('/error/missing_scopes_gmail')

    if user_creds_arent_intact(user_creds):
        return redirect('/error/invalid_credentials')

    # get user account information (email, pfp, etc)
    user_info = await gmail.get_user_info(user_creds)

    if user_info.error:
        logger.info(f'(`/gmail/callback` error) {user_info.error}')
        return redirect('/error/auth_error')

    await add_user_creds(user, user_info, user_creds)

    # watch inbox for new emails
    await gmail.watch_user_inbox(user_creds=user_creds)

    return next_or_fallback()  # redirect user to home or next page


@gmail_bp.route('/gmail/push', methods=['POST'])
async def gmail_push():
    # for an extra layer of security, check if the token parameter
    # of the uri matches with the configured environment variable
    token_arg = request.args.get('token')

    if token_arg != os.getenv('gmail_push_route_token'):
        logger.info('(`/gmail/push` denied) Invalid URL parameter `token`')
        return {'success': False, 'reason': 'Invalid URL parameter `token`'}

    try:
        # get jwt token from authorization header ("Bearer xxx")
        bearer_token = request.headers.get("Authorization")
        token = bearer_token.split(" ")[1]

    except (AttributeError, IndexError, jwt.DecodeError):
        logger.info('(`/gmail/push` denied) Invalid authorization header.')
        return {'success': False, 'reason': 'Invalid authorization header.'}

    # obtain signing key from jwt token
    signing_key = jwt_client.get_signing_key_from_jwt(token)

    try:
        # decode and verify the token
        jwt.decode(
            jwt=token,
            key=signing_key.key,
            algorithms=['RS256'],
            audience=jwt_audience,
            options={"verify_exp": True, "strict_aud": True},
        )
    except jwt.InvalidSignatureError:
        logger.info('(`/gmail/push` denied) Invalid signature for signed JWT header!')
        return {'success': False, 'reason': 'Invalid JWT signature.'}
    except jwt.ExpiredSignatureError:
        logger.info('(`/gmail/push` denied) Expired signature for signed JWT header!')
        return {'success': False, 'reason': 'Expired JWT signature.'}

    try:
        gmail_received_notify_user(await request.get_json())
    except ConnectionRefusedError:
        # bot is offline
        logger.info('(`/gmail/push` failed) socket connection refused')
        return {'success': False, 'reason': 'Internal server error'}, 500

    return {'success': True}
