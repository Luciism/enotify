import json
import socket
from base64 import b64decode
from typing import Any

from quart import current_app, request
from quart.sessions import SecureCookieSessionInterface

from notilib import config


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


# i couldn't figure out what the fuck to name this function
def gmail_received_notify_user(res_data: dict) -> None:
    data = res_data.get('message', {}).get('data')
    if not data:
        return

    decoded_data: dict = json.loads(b64decode(data).decode())
    email_address: str = decoded_data.get('emailAddress')

    if email_address is not None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('127.0.0.1', config('global.gmail_receive_socket_port')))
            client.send(email_address.encode())
