import logging
import os
import re
from base64 import b64decode

from aiogoogle import Aiogoogle, GoogleAPI
from aiogoogle.auth import UserCreds
from asyncpg import Connection

from .credentials import (
    load_user_credentials,
    client_creds
)
from .email_addresses import GmailEmailAddress
from ...database import Database, ensure_connection


logger = logging.getLogger(__name__)


class EmailPayloadHeader:
    def __init__(self, header_data: dict) -> None:
        self.raw: dict = header_data

        self.name: str = header_data.get('name')
        self.value: str = header_data.get('value')


class EmailPayloadBody:
    def __init__(self, body_data: dict) -> None:
        self.raw: dict = body_data

        self.size: int = body_data.get('size')
        self.data: str = body_data.get('data')

        self._decoded_data = None

    @property
    def decoded_data(self) -> str:
        if self._decoded_data is None:
            self._decoded_data = b64decode(self.data).decode()
        return self._decoded_data


class EmailPayloadPart:
    def __init__(self, part_data: dict) -> None:
        self.raw: dict = part_data

        self.part_id: str = part_data.get('partId')
        self.mime_type: str = part_data.get('mimeType')
        self.filename: str = part_data.get('filename')

        self._headers = None
        self._body = None

    @property
    def headers(self) -> list[EmailPayloadHeader]:
        if self._headers is None:
            self._headers = []
            for header in self.raw.get('headers', []):
                self._headers.append(EmailPayloadHeader(header))
        return self._headers

    @property
    def body(self) -> EmailPayloadBody:
        if self._body is None:
            self._body = EmailPayloadBody(self.raw.get('body'))
        return self._body


class EmailPayload:
    def __init__(self, payload_data: dict) -> None:
        self.raw: dict = payload_data

        self.part_id: str = payload_data.get('partId')
        self.mime_type: str = payload_data.get('mineType')
        self.filename: str = payload_data.get('filename')

        self._headers = None
        self._parts = None
        self._body = None

    @property
    def headers(self) -> list[EmailPayloadHeader]:
        if self._headers is None:
            self._headers = []
            for header in self.raw.get('headers', []):
                self._headers.append(EmailPayloadHeader(header))
        return self._headers

    @property
    def parts(self) -> list[EmailPayloadPart]:
        if self._parts is None:
            self._parts = []
            for header in self.raw.get('parts', []):
                self._parts.append(EmailPayloadPart(header))
        return self._parts

    @property
    def body(self) -> EmailPayloadBody:
        if self._body is None:
            self._body = EmailPayloadBody(self.raw.get('body'))
        return self._body


class Email:
    def __init__(self, email_data: dict) -> None:
        self.raw: dict = email_data

        self.id: str = email_data.get('id')
        self.thread_id: str = email_data.get('threadId')
        self.history_id: str = email_data.get('historyId')
        self.label_ids: list = email_data.get('labelIds', [])

        self.snippet: str = email_data.get('snippet')

        self.size_estimate: int = email_data.get('sizeEstimate')

        self.internal_date: str = email_data.get('internalDate')

        self._payload = None

        self._sender = None

    @property
    def payload(self) -> EmailPayload:
        if self._payload is None:
            self._payload = EmailPayload(self.raw.get('payload'))
        return self._payload

    @property
    def sender(self) -> str:
        """The sender of the email for example `Sender <sender@example.com>`"""
        if self._sender is None:
            for header in self.payload.headers:
                if header.name == 'From':
                    self._sender = header.value
                    break
        return self._sender


async def __retrieve_email_ids(
    count: int | None,
    google: Aiogoogle,
    gmail: GoogleAPI=None
) -> list[str]:
    """
    Retrieves a specified amount of email ids from a user's inbox
    :param count: the total amount of email ids to retrieve
    :param google: the Aiogoogle object built with the user's oauth\
        credentials to use
    :param gmail: the gmail discovery document to use, if left as `None`\
        one will automatically be acquired
    """
    if gmail is None:
        gmail = await google.discover("gmail", "v1")

    response = await google.as_user(
        gmail.users.messages.list(userId="me", maxResults=count)
    )

    return [message['id'] for message in response['messages']]


async def __retrieve_emails(
    google: Aiogoogle,
    count: int | None=None,
    email_ids: list[str] = None,
) -> list[Email]:
    """
    Retrieve x amount of emails the Aiogoogle `google` object
    :param google: the `aiogoogle.Aiogoogle` object to fetch the emails with
    :param count: the total amount of emails to fetch\
        (if `email_ids` is not provided)
    :param email_ids: a custom list of email ids to fetch the emails of
    Note that either `count` or `email_ids` should be passed
    """
    gmail = await google.discover("gmail", "v1")  # kms

    # fetch x amount of most recent email ids
    if email_ids is None:
        email_ids = await __retrieve_email_ids(count, google, gmail)

    # fetch actual email data via email ids
    emails = [
        Email(await google.as_user(gmail.users.messages.get(userId="me", id=email_id)))
        for email_id in email_ids
    ]
    return emails


async def retrieve_emails(
    user_creds: UserCreds,
    count: int | None=None
) -> Email | list[Email]:
    """
    Retrieves a specified amount of emails from a user's inbox
    :param user_creds: the google oauth credentials of the user
    :param count: the total amount of emails to retrieve
    """
    async with Aiogoogle(
        user_creds=user_creds,
        client_creds=client_creds
    ) as google:
        emails = await __retrieve_emails(google, count=count)

    # return singular email object if there is only one
    if len(emails) == 1:
        return emails[0]

    return emails


@ensure_connection
async def get_latest_email_id(
    email_address: str,
    conn: Connection=None
) -> str | None:
    """
    Gets the id of the latest email fetched for the specified email address.
    :param email_address: the email address to get the latest email id of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    latest_email_id = await conn.fetchval(
        'SELECT latest_email_id FROM gmail_credentials '
        'WHERE pgp_sym_decrypt(email_address, $2) = $1',
        email_address, os.getenv('database_encryption_key')
    )
    return latest_email_id


@ensure_connection
async def set_latest_email_id(
    email_address: str,
    latest_email_id: str=None,
    conn: Connection=None
) -> None:
    """
    Sets the `latest_email_id` value for an email address, if `latest_email_id`
    is left as `None`, the most id of the most recent email in the user's inbox
    inbox will be used. (Provided that the user has valid credentials).
    :param email_address: the email address to set the latest email id for
    :param latest_email_id: the actual latest email id value to set
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    # obtain latest email id from users inbox if it is None
    if latest_email_id is None:
        user_creds = await load_user_credentials(email_address, conn=conn)
        if user_creds is None:
            raise NotImplementedError(
                'Invalid user credentials, either pass `latest_email_id` '
                'or ensure that there are valid user creds bound to that email address!')

        async with Aiogoogle(
            user_creds=user_creds,
            client_creds=client_creds
        ) as google:
            latest_email_ids = await __retrieve_email_ids(count=1, google=google)

            if not latest_email_ids:
                raise NotImplementedError(
                    'Failed to fetch the latest email id from the users inbox!')
            latest_email_id = latest_email_ids[0]

    # check if row exists in database
    existing = await conn.fetchval(
        'SELECT email_address FROM gmail_credentials '
        'WHERE pgp_sym_decrypt(email_address, $2) = $1',
        email_address, os.getenv('database_encryption_key')
    )

    # should typically always exist if this function is called, but shit happens
    if existing is None:
        await conn.execute(
            'INSERT INTO gmail_credentials (email_address, latest_email_id, valid) '
            'VALUES (pgp_sym_encrypt($1, $3), $2, false)',
            email_address, latest_email_id, os.getenv('database_encryption_key')
        )  # insert new row and set `valid` to false because there are no credentials
        return

    await conn.execute(
        'UPDATE gmail_credentials SET latest_email_id = $1 '
        'WHERE pgp_sym_decrypt(email_address, $2) = $3',
        latest_email_id, os.getenv('database_encryption_key'), email_address
    )


@ensure_connection
async def __check_latest_email_id(
    email_address: str,
    email_id: str,
    conn: Connection=None
) -> bool:
    latest_email_id = await get_latest_email_id(email_address, conn=conn)

    if latest_email_id == email_id:
        return True
    return False


async def retrieve_new_email(email_address: str) -> Email | None:
    """
    This function is intended to be used to retrieve the email in order to
    send a new email notification to a user.
    Retrieves the most recent email from a user's inbox if it has not already
    been retrieved in the past.
    :param email_address: the email address of the inbox to retrieve the email of
    """
    pool = await Database().connect()

    async with pool.acquire() as conn:
        user_creds = await load_user_credentials(email_address, conn=conn)

        if user_creds is None:
            logger.debug('No credentials found or specified email address.')
            return None

        async with Aiogoogle(
            user_creds=user_creds,
            client_creds=client_creds
        ) as google:
            gmail = await google.discover("gmail", "v1")

            email_id = await __retrieve_email_ids(count=1, google=google, gmail=gmail)
            if not email_id:
                logger.debug('Failed to obtain a valid email id.')
                return None

            email_id = email_id[0]  # `__retrieve_email_ids` returns a list of email ids

            # whether the fetched email id matches the locally stored "latest email id"
            email_id_matches = await __check_latest_email_id(
                email_address, email_id, conn=conn)

            if email_id_matches:  # email has already been retrieved
                logger.debug('Email has already been retrieved.')
                return None

            # fetch actual email
            email = await __retrieve_emails(google, email_ids=[email_id])

            await set_latest_email_id(email_address, email_id, conn=conn)

    if email:
        return email[0]  # email is a list of emails
    return None


async def check_filters(
    discord_id: str,
    email_address: str,
    email: Email,
) -> bool:
    """
    Checks if a user wants to be notified of an incoming email based on
    the filters they have set
    :param discord_id: the discord id of the user that will be notified
    :param email_address: the email address of the recipient of the incoming email
    :param email: the email data of the incoming email
    """
    gmail_address = GmailEmailAddress(discord_id, email_address)

    # sender whitelist is enabled
    if await gmail_address.filters.sender_whitelist_enabled is True:
        # extract email address portion of email sender
        # for example, extract `sender@example.com` from `Sender <sender@example.com>`
        match = re.search(r'<(.*)>', email.sender)
        sender = match.group(1) if match else email.sender

        # sender is not whitelisted
        if not sender.lower() in await gmail_address.filters.whitelisted_senders:
            return False

    # all checks passed
    return True
