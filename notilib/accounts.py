"""Accounts system logic"""


from datetime import datetime
from typing import NamedTuple

import asyncpg

from .functions import create_query_placeholders
from .database import ensure_connection
from .exceptions import ConfirmationError


class AccountDataTuple(NamedTuple):
    """Account data named tuple"""
    account_id: int
    discord_id: int
    creation_timestamp: float
    permissions: str
    blacklisted: int


@ensure_connection
async def create_account(
    discord_id: int,
    account_id: int=None,
    creation_timestamp: float=None,
    permissions: list | str=None,
    blacklisted: bool=False,
    conn: asyncpg.Pool=None
) -> bool:
    """
    Creates a new account for a user if ones doesn't already exist
    :param discord_id: the discord id of the respective user
    :param account_id: override the autoincrement account id
    :param creation_timestamp: override the creation timestamp of the account
    :param permissions: set the permissions for the user
    :param blacklisted: set whether the accounts is blacklisted
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically

    :return: bool of whether or not the account was created
    """
    existing_account = await conn.fetchrow(
        'SELECT * FROM accounts WHERE discord_id = $1', discord_id)

    # return if account exists
    if existing_account:
        return False

    if creation_timestamp is None:
        creation_timestamp = datetime.utcnow().timestamp()

    # keys are columns, values are values
    data = {
        'discord_id': discord_id,
        'creation_timestamp': creation_timestamp,
        'blacklisted': int(blacklisted)
    }

    # if a custom account id is provided, add it to the data
    if account_id:
        data['account_id'] = account_id

    # if a custom permission set is provided, add it to the data
    if permissions:
        # if the permissions are a list, convert it to a comma seperated list
        if isinstance(permissions, list):
            permissions = ','.join(permissions)
        data['permissions'] = permissions

    # join the column names and placeholder values
    column_names = ', '.join(data.keys())
    placeholders = create_query_placeholders(len(data.values()))

    await conn.execute(
        f'INSERT INTO accounts ({column_names}) VALUES ({placeholders})',
        *tuple(data.values()))

    return True


@ensure_connection
async def delete_account(
    discord_id: int,
    confirm: bool=False,
    conn: asyncpg.Pool=None
) -> None:
    """
    Entirely erase an account from existence
    :param discord_id: the discord id of the account to delete
    :param confirm: must `True` in order to delete the account
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    # raise error if deletion is unconfirmed (making it harder to slip up)
    if confirm is False:
        raise ConfirmationError(
            'Param `confirm` must be `True` in order to delete an account!')

    await conn.execute('DELETE FROM accounts WHERE discord_id = $1', discord_id)


async def __select_account_data(discord_id: int, conn: asyncpg.Connection):
    return await conn.fetchrow(
        'SELECT * FROM accounts WHERE discord_id = $1', discord_id)


@ensure_connection
async def get_account(
    discord_id: int,
    create: bool=False,
    conn: asyncpg.Pool=None
) -> AccountDataTuple | None:
    """
    Gets the account data for a user
    :param discord_id: the discord id of the user to get the account data for
    :param create: if an account should be created if one does not already exists
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically
    """
    account_data = await __select_account_data(discord_id, conn)

    if account_data is None:
        # return no data if "create if not exists" is False
        if not create:
            return None

        # create account and select account data
        await create_account(discord_id)
        account_data = await __select_account_data(discord_id, conn)

    # return account data tuple as a named tuple
    return AccountDataTuple(*account_data)


@ensure_connection
async def set_account_blacklist(
    discord_id: int,
    blacklisted: bool=True,
    create: bool=True,
    conn: asyncpg.Pool=None
) -> None:
    """
    Set the blacklist property of an account
    :param discord_id: the discord id of the user account
    to modify the blacklist of
    :param blacklisted: whether to blacklist or unblacklist the user
    :param create: whether or not to create the account if it doesn't exist
    """
    # check if account exists
    account_data = await __select_account_data(discord_id, conn)
    if not account_data:
        # create account with blacklist setting if "create if not exists" is true
        if create:
            await create_account(discord_id, blacklisted=blacklisted, conn=conn)
        return

    # update existing account blacklist value
    await conn.execute(
        'UPDATE accounts SET blacklisted = $1 WHERE discord_id = $2',
        int(blacklisted), discord_id)