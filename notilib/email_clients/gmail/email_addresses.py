import os

from asyncpg import Connection

from notilib import ensure_connection, create_account


@ensure_connection
async def get_email_addresses(
    discord_id: int,
    conn: Connection=None
) -> list[str]:
    """
    Returns a list of email addresses associated with the provided discord id
    :param discord_id: the discord id to find the respective email addresses of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    email_addresses = await conn.fetchval(
        'SELECT decrypt_array(gmail_email_addresses, $2) AS gmail_email_addresses '
        'FROM accounts WHERE discord_id = $1',
        discord_id, os.getenv('database_encryption_key')
    )
    return email_addresses or []


@ensure_connection
async def add_email_address(
    discord_id: int,
    email_address: str,
    conn: Connection=None
) -> None:
    """
    Adds an email address to an account's list of email addresses
    :param discord_id: the discord id of the account to add an email address to
    :param email_address: the email address to add to the account
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    existing = await conn.fetchval(
        'SELECT account_id FROM accounts WHERE discord_id = $1', discord_id)

    if existing is None:
        # create account with x email address
        await create_account(
            discord_id=discord_id,
            gmail_email_addresses=[email_address],
            conn=conn
        )
        return

    current_email_addresses = await get_email_addresses(discord_id, conn=conn)

    # avoid duplicates
    if email_address not in current_email_addresses:
        await conn.execute(
            'UPDATE accounts SET gmail_email_addresses = '
                'gmail_email_addresses || pgp_sym_encrypt($1, $3) '
            'WHERE discord_id = $2',
            email_address, discord_id, os.getenv('database_encryption_key')
        )


@ensure_connection
async def remove_email_address(
    discord_id: int,
    email_address: str,
    conn: Connection=None
) -> None:
    """
    Removes a specified email address from a user account
    :param discord_id: the discord id of the respective user account
    :param email_address: the email address to remove from the account
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    existing = await conn.fetchval(
        'SELECT account_id FROM accounts WHERE discord_id = $1', discord_id)

    if existing is None:  # account not found
        return

    await conn.execute(
        'UPDATE accounts '
        'SET gmail_email_addresses = '
            'remove_encrypted_array_element($1, gmail_email_addresses, $3) '
        'WHERE discord_id = $2',
        email_address, discord_id, os.getenv('database_encryption_key')
    )


@ensure_connection
async def email_address_to_discord_ids(
    email_address: str,
    conn: Connection=None
) -> list[int]:
    """
    Returns a list of discord ids that have a certain email tied to them
    :param email_address: the email address to find the respective discord ids of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    rows = await conn.fetch(
        'SELECT discord_id FROM accounts '
        'WHERE decrypt_array(gmail_email_addresses, $2) @> ARRAY[$1]',
        email_address, os.getenv('database_encryption_key')
    )

    return [row['discord_id'] for row in rows]
