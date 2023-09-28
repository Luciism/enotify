"""A permissions system"""


from .functions import comma_separated_to_list
from .accounts import create_account, get_account
from .database import Database


async def get_permissions(discord_id: int) -> list:
    """
    Returns list of permissions for a discord user
    :param discord_id: the discord id of the respective user
    """
    account_data = await get_account(discord_id, create=True)

    if account_data:
        # convert comma seperated list of permissions to list
        return comma_separated_to_list(account_data.permissions)
    return []


async def has_permission(
    discord_id: int,
    permissions: str | list[str],
    allow_star: bool=True
) -> bool:
    """
    Returns bool `True` or `False` if a user has a permission
    :param discord_id: the discord id of the respective user
    :param permissions: the permission(s) to check for. if multiple permissions
        are provided, `True` will be returned if the user has
        at least one of the given permissions.
    :param allow_star: returns `True` if the user has the `*` permission
    """
    user_permissions = await get_permissions(discord_id)

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


async def set_permissions(discord_id: int, permissions: list | str):
    """
    Sets a users permissions to the given permissions\n
    Permissions can either be a list of permissions as a list
    or as a string with commas `,` as seperators
    :param discord_id: the discord id of the respective user
    :param permissions: the permissions to set for the user
    """
    # join list of permissions into a comma seperated list
    if isinstance(permissions, list):
        permissions = ','.join(permissions)

    db = Database()
    await db.connect()

    account_data = await db.conn.execute(
        'SELECT account_id FROM accounts WHERE discord_id = $1', discord_id)

    if account_data:
        # if account exists, update the account's permissions
        await db.conn.execute(
            'UPDATE accounts SET permissions = $1 WHERE discord_id = $2',
            permissions, discord_id
        )
    else:
        # otherwise create a new account with the correct permissions
        await create_account(discord_id, permissions=permissions)


async def add_permission(discord_id: int, permission: str):
    """
    Adds a permission to a user if they don't already have it
    :param discord_id: the discord id of the respective user
    :param permission: the permission to add to the user
    """
    permissions = await get_permissions(discord_id)

    # if the user doesnt already have the permission, add it
    if not permission in permissions:
        permissions.append(permission)
        await set_permissions(discord_id, permissions)


async def remove_permission(discord_id: int, permission: str):
    """
    Removes a permission for a user if they have it
    :param discord_id: the discord id of the respective user
    :param permission: the permission to remove from the user
    """
    permissions = await get_permissions(discord_id)

    # if user has permission, recursively remove all instances of that
    # permission from the list of permissions
    if permission in permissions:
        while permission in permissions:
            permissions.remove(permission)
        await set_permissions(discord_id, permissions)


class PermissionManager:
    def __init__(self, discord_id: int):
        self.discord_id = discord_id


    async def add_permission(self, permission: str):
        """
        Adds a permission to a user if they don't already have it
        :param permission: the permission to add to the user
        """
        await add_permission(self.discord_id, permission)


    async def remove_permission(self, permission: str):
        """
        Removes a permission for a user if they have it
        :param permission: the permission to remove from the user
        """
        await remove_permission(self.discord_id, permission)


    async def set_permissions(self, permissions: list | str):
        """
        Sets a users permissions to the given permissions\n
        Permissions can either be a list of permissions as a list
        or as a string with commas `,` as seperators
        :param permissions: the permissions to set for the user
        """
        await set_permissions(self.discord_id, permissions)


    async def get_permissions(self):
        """Returns list of permissions for a discord user"""
        return await get_permissions(self.discord_id)


    async def has_permission(
        self,
        permissions: str | list[str],
        allow_star: bool=True
    ) -> bool:
        """
        Returns bool `True` or `False` if a user has a permission
        :param permission: the permission to check for
        :param allow_star: returns `True` if the user has the `*` permission
        """
        return await has_permission(self.discord_id, permissions, allow_star)
