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


gmail_bp = Blueprint(
    name='gmail',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/gmail/'
)

oauth2 = Oauth2Manager(client_creds=gmail.client_creds)


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
