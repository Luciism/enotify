import os

from asyncpg import Connection

from .common import WebmailServiceLiteral
from .database import ensure_connection


@ensure_connection
async def get_email_addresses(
    discord_id: int,
    webmail_service: WebmailServiceLiteral,
    conn: Connection=None
) -> list[str]:
    """
    Returns a list of email addresses associated with the provided discord id
    :param discord_id: the discord id to find the respective email addresses of
    :param webmail_service: ...
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    rows = await conn.fetch(
        'SELECT pgp_sym_decrypt(email_address, $3) AS email_address '
        "FROM email_notification_filters WHERE discord_id = $1 AND webmail_service = $2",
        discord_id, webmail_service, os.getenv('database_encryption_key')
    )

    email_addresses = [row['email_address'] for row in rows]
    return email_addresses


@ensure_connection
async def get_all_email_addresses(
    discord_id: int,
    conn: Connection=None
) -> list[dict[str, str]]:
    """
    Returns a list of email addresses associated with the provided discord id\
        regardless of the webmail service
    :param discord_id: the discord id to find the respective email addresses of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    email_addresses = await conn.fetch(
        'SELECT pgp_sym_decrypt(email_address, $2) AS email_address, webmail_service '
        "FROM email_notification_filters WHERE discord_id = $1",
        discord_id, os.getenv('database_encryption_key')
    )

    return email_addresses


@ensure_connection
async def add_email_address(
    discord_id: int,
    email_address: str,
    webmail_service: WebmailServiceLiteral,
    conn: Connection=None
) -> None:
    """
    Adds an email address to an account's list of email addresses
    :param discord_id: the discord id of the account to add an email address to
    :param email_address: the email address to add to the account
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    current_email_addresses = await get_email_addresses(
        discord_id, webmail_service=webmail_service, conn=conn)

    if email_address in current_email_addresses:
        # email address already added
        return

    await conn.execute(
        'INSERT INTO email_notification_filters (discord_id, email_address, webmail_service) '
        "VALUES ($1, pgp_sym_encrypt($2, $4), $3)",
        discord_id, email_address, webmail_service, os.getenv('database_encryption_key')
    )

@ensure_connection
async def remove_email_address(
    discord_id: int,
    email_address: str,
    webmail_service: WebmailServiceLiteral,
    conn: Connection=None
) -> None:
    """
    Removes a specified email address from a user account
    :param discord_id: the discord id of the respective user account
    :param email_address: the email address to remove from the account
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    await conn.execute(
        "DELETE FROM email_notification_filters WHERE discord_id = $1 "
        "AND pgp_sym_decrypt(email_address, $4) = $2 AND webmail_service = $3",
        discord_id, email_address, webmail_service,
        os.getenv('database_encryption_key')
    )


@ensure_connection
async def email_address_to_discord_ids(
    email_address: str,
    webmail_service: WebmailServiceLiteral,
    conn: Connection=None
) -> list[int]:
    """
    Returns a list of discord ids that have a certain email tied to them
    :param email_address: the email address to find the respective discord ids of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    rows = await conn.fetch(
        'SELECT discord_id FROM email_notification_filters '
        "WHERE pgp_sym_decrypt(email_address, $3) = $1 AND webmail_service = $2",
        email_address, webmail_service, os.getenv('database_encryption_key')
    )

    return [row['discord_id'] for row in rows]
