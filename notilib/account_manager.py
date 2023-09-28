"""The accounts system manager class"""


from datetime import datetime

from .accounts import get_account, set_account_blacklist, create_account
from .permissions import has_permission, PermissionManager
from .functions import comma_separated_to_list


class AccountDeleteConfirm:
    async def confirm(self):
        raise NotImplementedError('Deletion system not implemented!')


class Account:
    def __init__(self, discord_id: int) -> None:
        """
        Internal account system management class
        :param discord_id: the discord id associated with the account
        """
        self.discord_id = discord_id

        self.refresh()


    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'discord_id={self.discord_id}, '
            f'account_id={self.account_id}, '
            f'creation_date="{self.creation_date}", '
            f'blacklisted={self.blacklisted})'
        )


    def refresh(self):
        """Refresh the class data"""
        # distiguishable default object
        self.__default = object()

        self._permission_manager = self.__default

        self._account_id = self.__default
        self._creation_timestamp = self.__default
        self._creation_date = self.__default
        self._permissions = self.__default
        self._blacklisted = self.__default
        self._exists = self.__default


    async def _load_account_table(self):
        if self._exists is False:
            return

        account = await get_account(self.discord_id)

        if account:
            self._exists = True

            self._account_id = account.account_id
            self._creation_timestamp = account.creation_timestamp
            self._permissions = comma_separated_to_list(account.permissions)
            self._blacklisted = bool(account.blacklisted)

            return

        self._exists = False


    async def create(self,
        account_id: int=None,
        creation_timestamp: float=None,
        permissions: list | str=None,
        blacklisted: bool=False
    ) -> None:
        """
        Creates a new account for a user if ones doesn't already exist
        :param account_id: override the autoincrement account id
        :param creation_timestamp: override the creation timestamp of the account
        :param permissions: set the permissions for the user
        :param blacklisted: set whether the accounts is blacklisted
        """
        await create_account(
            discord_id=self.discord_id,
            account_id=account_id,
            creation_timestamp=creation_timestamp,
            permissions=permissions,
            blacklisted=blacklisted
        )


    def delete(self) -> AccountDeleteConfirm:
        """Delete the account (NOT IMPLEMENTED)"""
        return AccountDeleteConfirm()


    async def set_blacklisted(self, blacklisted: bool=True):
        """Blacklists or unblacklists the account"""
        await set_account_blacklist(self.discord_id, blacklisted)


    async def has_permission(
        self,
        permissions: str | list,
        allow_star: bool=True
    ) -> bool:
        """
        Returns bool `True` or `False` if a user has a permission
        :param permissions: the permission(s) to check for. if multiple permissions
            are provided, `True` will be returned if the user has
            at least one of the given permissions.
        :param allow_star: returns `True` if the user has the `*` permission
        """
        return await has_permission(self.discord_id, permissions, allow_star)


    @property
    async def account_id(self) -> float:
        """The internal account system assigned account ID of the account"""
        if self._account_id is self.__default:
            await self._load_account_table()
        return self._account_id

    @property
    async def creation_timestamp(self) -> float:
        """The timestamp when the account was created (UTC time)"""
        if self._creation_timestamp is self.__default:
            await self._load_account_table()
        return self._creation_timestamp

    @property
    async def creation_date(self) -> str | None:
        """The date when the account was created in format `%d/%m/%Y` (UTC time)"""
        if self._creation_date is self.__default:
            creation_timestamp = await self.creation_timestamp

            if creation_timestamp:
                creation = datetime.utcfromtimestamp(creation_timestamp)
                self._creation_date = creation.strftime('%d/%m/%Y')
            else:
                self._creation_date = None
        return self._creation_date

    @property
    async def permissions(self) -> list:
        """A list of custom permissions that the user has"""
        if self._permissions is self.__default:
            await self._load_account_table()
        return self._permissions

    @property
    async def blacklisted(self) -> bool:
        """`True` or `False` whether the user is blacklisted"""
        if self._blacklisted is self.__default:
            await self._load_account_table()
        return self._blacklisted

    @property
    async def exists(self) -> bool:
        """`True` or `False` whether the account exists"""
        if self._exists is self.__default:
            await self._load_account_table()
        return self._exists

    @property
    def permission_manager(self) -> PermissionManager:
        """A permissions manager for the account"""
        if self._permission_manager is self.__default:
            self._permission_manager = PermissionManager(self.discord_id)
        return self._permission_manager
