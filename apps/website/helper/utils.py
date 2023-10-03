from typing import Any

from flask import current_app, request
from flask.sessions import SecureCookieSessionInterface


def decrypt_session_cookie(session_cookie: str=None) -> dict | Any:
    """
    Returns the raw decrypted session cookie data
    :param session_cookie: the raw encrypted session cookie value
    """
    if session_cookie is None:
        session_cookie = request.cookies.get('session')

    if session_cookie is None:
        return {}

    sscsi = SecureCookieSessionInterface()
    signingSerializer = sscsi.get_signing_serializer(current_app)

    return signingSerializer.loads(session_cookie)
