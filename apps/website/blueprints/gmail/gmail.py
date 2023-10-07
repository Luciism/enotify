import os
import logging
from urllib.parse import urljoin

import jwt
from aiogoogle import HTTPError
from aiogoogle.auth import UserCreds
from aiogoogle.auth.managers import Oauth2Manager
from quart import (
    Blueprint,
    redirect,
    request,
    session
)

from notilib import Database
from notilib.email_clients import gmail
from helper import fetch_discord_user, decrypt_session_cookie


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')

jwt_client = jwt.PyJWKClient('https://www.googleapis.com/oauth2/v2/certs')
oauth2 = Oauth2Manager(client_creds=gmail.client_creds)

jwt_audience = urljoin(os.getenv('base_url'), '/gmail/push')


gmail_bp = Blueprint(
    name='gmail',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/gmail/'
)


@gmail_bp.route('/gmail/authorize')
async def authorize():
    uri = oauth2.authorization_url(
        client_creds=gmail.client_creds,
        state=request.cookies.get('session')
    )
    return redirect(uri)


@gmail_bp.route('/gmail/callback')
async def callback():
    # session cookie stored in `state` url param
    state = request.args.get('state')
    session_cookie = decrypt_session_cookie(state)

    if not session_cookie:
        return 'Failed to fetch discord information'

    # loop through all the decrypted items in session_cookie
    # and add them back to the session
    for key, value in session_cookie.items():
        session[key] = value

    # make sure the user is logged in
    access_token = session.get('access_token')
    user = await fetch_discord_user(access_token, cache=True)

    if user is None:
        return 'Failed to fetch discord information'

    # Handle errors
    if request.args.get('error'):
        error = {
            'error': request.args.get('error'),
            'error_description': request.args.get('error_description')
        }
        return error

    # Exchange code for the access and refresh token
    if request.args.get('code'):
        # build user creds from grant query parameter
        try:
            user_creds: UserCreds = await oauth2.build_user_creds(
                grant=request.args.get('code'),
                client_creds=gmail.client_creds
            )
        except HTTPError:
            return 'Invalid grant!'

        # get user account information (email, pfp, etc)
        user_info = await gmail.get_user_info(user_creds)

        if user_info.error:
            # handle error
            return user_info.error

        await gmail.save_user_credentials(user.id, user_info.email, user_creds)

        await Database().cleanup()
        return user_creds

    # Should either receive a code or an error
    return "Unable to obtain grant, please try again."


@gmail_bp.route('/gmail/push', methods=['POST'])
async def gmail_push():
    try:
        # get jwt token from authorization header ("Bearer xxx")
        bearer_token = request.headers.get("Authorization")
        token = bearer_token.split(" ")[1]

        # get unverified header in order to find the algorithm to use
        unverified_header = jwt.get_unverified_header(token)
    except (AttributeError, IndexError, jwt.DecodeError):
        logger.info('(`/gmail/push`) Invalid authorization header.')
        return {'success': False, 'reason': 'Invalid authorization header.'}

    # obtain signing key from jwt token
    signing_key = jwt_client.get_signing_key_from_jwt(token)

    try:
        # decode and verify the token
        jwt.decode(
            token,
            signing_key.key,
            algorithms=[unverified_header['alg']],
            audience=jwt_audience,
            options={"verify_exp": True, "strict_aud": True},
        )
    except jwt.InvalidSignatureError:
        logger.info('(`/gmail/push`) Invalid signature for signed JWT header!')
        return {'success': False, 'reason': 'Invalid JWT signature.'}
    except jwt.ExpiredSignatureError:
        logger.info('(`/gmail/push`) Expired signature for signed JWT header!')
        return {'success': False, 'reason': 'Expired JWT signature.'}

    print(await request.get_json())

    return {'success': True}


@gmail_bp.route('/gmail/creds')
async def gmail_creds():
    email_address = request.args.get('email')
    access_token = session.get('access_token')

    user = await fetch_discord_user(access_token, cache=True)
    return await gmail.load_user_credentials(user.id, email_address) or "no data"
