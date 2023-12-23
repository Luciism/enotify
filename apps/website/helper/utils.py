import os
import json
import socket
from base64 import b64decode
from typing import Any, TypedDict

from email_validator import validate_email, EmailSyntaxError, EmailNotValidError
from quart import current_app, request
from quart.sessions import SecureCookieSessionInterface

from notilib import config


APP_PATH = os.path.abspath(f'{__file__}/../..')


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
            client.connect(('127.0.0.1', config('global.gmail.receive_socket_port')))
            client.send(email_address.encode())


class ResponseMsg(TypedDict):
    message: str
    color: str
    success: bool


class _ResponseMsgs:
    def __init__(self) -> None:
        self._data = None

    @property
    def data(self) -> dict[str, dict[str, dict]]:
        if self._data is None:
            with open(f'{APP_PATH}/responses.json', 'r') as df:
                self._data = json.load(df)
        return self._data

__response_msgs = _ResponseMsgs()


def response_msg(response: str, forced_color: str=None) -> ResponseMsg | dict:
    """
    Returns a certain response from the `responses.json` file
    with the dynamically set color
    :param response: the key for the response data to return
    :param forced_color: a hex code to force the color to be set as
    """
    responses = __response_msgs.data

    response_data = responses.get('responses', {}).get(response, {})

    # get the color value from the color name in the response data
    if forced_color is None:
        response_color = response_data.get('color', 'white')
        color_hex = responses.get('colors', {}).get(response_color, '#FFFFFF')
        response_data['color'] = color_hex
    else:
        response_data['color'] = forced_color

    # if the json data is for some reason missing
    if response_data.get('message') is None:
        response_data['message'] = response

    return response_data


def is_email_address_valid(email_address: str) -> bool:
    """
    Checks if an email address syntax is valid or not
    :param email_address: the email address to validate
    :return bool: whether the email address is valid
    """
    try:
        validate_email(email_address)
        return True
    except (EmailNotValidError, EmailSyntaxError):
        return False
