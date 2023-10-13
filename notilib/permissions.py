"""A permissions system"""

from asyncpg import Connection

from .accounts import create_account, get_account
from .database import ensure_connection


@ensure_connection
async def get_permissions(discord_id: int, conn: Connection=None) -> list:
    """
    Returns list of permissions for a discord user
    :param discord_id: the discord id of the respective user
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    account_data = await get_account(discord_id, create=True, conn=conn)

    if account_data:
        return account_data.permissions or []
    return []


@ensure_connection
async def has_permission(
    discord_id: int,
    permissions: str | list[str],
    allow_star: bool=True,
    conn: Connection=None
) -> bool:
    """
    Returns bool `True` or `False` if a user has a permission
    :param discord_id: the discord id of the respective user
    :param permissions: the permission(s) to check for. if multiple permissions
        are provided, `True` will be returned if the user has
        at least one of the given permissions.
    :param allow_star: returns `True` if the user has the `*` permission
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    user_permissions = await get_permissions(discord_id, conn=conn)

    # return True to any permissions if the user has the "*" permission
    # and star permissions are allowed
    if allow_star and '*' in user_permissions:
        return True

    # convert permissions to a list if it is a singular string
    if isinstance(permissions, str):
        permissions = [permissions]

    # at least one permission is in user_permissions
    if set(permissions) & set(user_permissions):
        return True

    return False


@ensure_connection
async def set_permissions(
    discord_id: int,
    permissions: list | str,
    conn: Connection=None
) -> None:
    """
    Sets a users permissions to the given permissions\n
    Permissions can either be a list of permissions as a list
    or as a string with commas `,` as seperators
    :param discord_id: the discord id of the respective user
    :param permissions: the permissions to set for the user
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    # join list of permissions into a comma seperated list
    if isinstance(permissions, str):
        permissions = [permissions]

    account_data = await conn.fetchrow(
        'SELECT account_id FROM accounts WHERE discord_id = $1', discord_id)

    if account_data:
        # if account exists, update the account's permissions
        await conn.execute(
            'UPDATE accounts SET permissions = $1 WHERE discord_id = $2',
            permissions, discord_id
        )
    else:
        # otherwise create a new account with the correct permissions
        await create_account(discord_id, permissions=permissions, conn=conn)


@ensure_connection
async def add_permission(
    discord_id: int,
    permission: str,
    conn: Connection=None
) -> None:
    """
    Adds a permission to a user if they don't already have it
    :param discord_id: the discord id of the respective user
    :param permission: the permission to add to the user
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    permissions = await get_permissions(discord_id, conn=conn)

    # if the user doesnt already have the permission, add it
    if not permission in permissions:
        permissions.append(permission)
        await set_permissions(discord_id, permissions, conn=conn)


@ensure_connection
async def remove_permission(
    discord_id: int,
    permission: str,
    conn: Connection=None
) -> None:
    """
    Removes a permission for a user if they have it
    :param discord_id: the discord id of the respective user
    :param permission: the permission to remove from the user
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    permissions = await get_permissions(discord_id, conn=conn)

    # if user has permission, recursively remove all instances of that
    # permission from the list of permissions
    if permission in permissions:
        while permission in permissions:
            permissions.remove(permission)
        await set_permissions(discord_id, permissions, conn=conn)


class PermissionManager:
    def __init__(
        self,
        discord_id: int
    ) -> None:
        """
        Main permission manager class
        :param discord_id: the discord id of the user to manage the permissions of
        """
        self.discord_id = discord_id


    async def add_permission(self, permission: str, conn: Connection=None) -> None:
        """
        Adds a permission to a user if they don't already have it
        :param permission: the permission to add to the user
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await add_permission(self.discord_id, permission, conn=conn)


    async def remove_permission(
        self,
        permission: str,
        conn: Connection=None
    ) -> None:
        """
        Removes a permission for a user if they have it
        :param permission: the permission to remove from the user
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await remove_permission(self.discord_id, permission, conn=conn)


    async def set_permissions(
        self,
        permissions: list | str,
        conn: Connection=None
    ) -> None:
        """
        Sets a users permissions to the given permissions\n
        Permissions can either be a list of permissions as a list
        or as a string with commas `,` as seperators
        :param permissions: the permissions to set for the user
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await set_permissions(self.discord_id, permissions, conn=conn)


    async def get_permissions(self, conn: Connection=None) -> list:
        """
        Returns list of permissions for a discord user
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        return await get_permissions(self.discord_id, conn=conn)


    async def has_permission(
        self,
        permissions: str | list[str],
        allow_star: bool=True,
        conn: Connection=None
    ) -> bool:
        """
        Returns bool `True` or `False` if a user has a permission
        :param permission: the permission to check for
        :param allow_star: returns `True` if the user has the `*` permission
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        return await has_permission(
            self.discord_id, permissions, allow_star, conn=conn)
