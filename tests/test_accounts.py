import pytest

from .utils import MockData
from notilib import (
    ConfirmationError,
    create_account,
    delete_account,
    get_account,
    set_account_blacklist
)


class TestAccountCreation:
    async def _create_account(self, conn, *args, **kwargs):
        account = await get_account(MockData.discord_id, conn=conn)
        if account:
            await delete_account(MockData.discord_id, confirm=True, conn=conn)

        # create and get account
        await create_account(MockData.discord_id, *args, **kwargs, conn=conn)
        account = await get_account(MockData.discord_id, conn=conn)

        # make sure account exists
        assert account is not None
        return account


    @pytest.mark.asyncio
    async def test_create_account_default(self, conn):
        await self._create_account(conn=conn)

    @pytest.mark.asyncio
    async def test_create_account_permissions(self, conn):
        account = await self._create_account(permissions=['foo', 'bar'], conn=conn)
        assert account.permissions == ['foo', 'bar']

    @pytest.mark.asyncio
    async def test_create_account_blacklisted(self, conn):
        account = await self._create_account(blacklisted=True, conn=conn)
        assert account.blacklisted == 1

    @pytest.mark.asyncio
    async def test_create_account_custom_id(self, conn):
        account = await self._create_account(account_id=123, conn=conn)
        assert account.account_id == 123

    @pytest.mark.asyncio
    async def test_create_account_creation_timestamp(self, conn):
        account = await self._create_account(creation_timestamp=123, conn=conn)
        assert account.creation_timestamp == 123


class TestAccountDeletion:
    async def _delete_account(self, confirmation: bool, conn):
        # make sure the account exists
        await create_account(MockData.discord_id, conn=conn)

        # delete the account and make sure it doesnt exist
        await delete_account(MockData.discord_id, confirm=confirmation, conn=conn)

        account = await get_account(MockData.discord_id, conn=conn)
        assert account is None


    @pytest.mark.asyncio
    async def test_delete_account_with_confirmation(self, conn):
        await self._delete_account(confirmation=True, conn=conn)

    @pytest.mark.asyncio
    async def test_delete_account_without_confirmation(self, conn):
        with pytest.raises(ConfirmationError):
            await self._delete_account(confirmation=False, conn=conn)


class TestAccountBlacklisting:
    @pytest.mark.asyncio
    async def test_blacklist_account_doesnt_exist_create(self, conn):
        """Test blacklisting an account that doesnt exist with
        the create if account doesn't exist parameter as true"""
        # make sure account doesn't exist
        await delete_account(MockData.discord_id, confirm=True, conn=conn)

        await set_account_blacklist(
            MockData.discord_id, blacklisted=True, create=True, conn=conn)

        account = await get_account(MockData.discord_id, conn=conn)

        assert account is not None
        assert account.blacklisted == 1


    @pytest.mark.asyncio
    async def test_blacklist_account_does_exist(self, conn):
        """Test blacklisting an existing account"""
        # make sure account does exist
        await create_account(MockData.discord_id, conn=conn)

        await set_account_blacklist(
            MockData.discord_id, blacklisted=True, conn=conn)

        account = await get_account(MockData.discord_id, conn=conn)

        assert account is not None
        assert account.blacklisted == 1


class TestGetAccount:
    @pytest.mark.asyncio
    async def test_get_account_doesnt_exist_do_create(self, conn):
        """Account doesn't exist, account will be created and returned"""
        # make sure account doesn't exist
        await delete_account(MockData.discord_id, confirm=True, conn=conn)

        await get_account(MockData.discord_id, create=True, conn=conn)

        # get account with seperate function call
        account = await get_account(MockData.discord_id, conn=conn)
        assert account is not None


    @pytest.mark.asyncio
    async def test_get_account_doesnt_exist_dont_create(self, conn):
        """Account doesn't exist, account will not be created and returned"""
        # make sure account doesn't exist
        await delete_account(MockData.discord_id, confirm=True, conn=conn)

        account = await get_account(MockData.discord_id, create=False, conn=conn)
        assert account is None


    @pytest.mark.asyncio
    async def test_get_account_exists_dont_create(self, conn):
        """Account exists, account will be directly fetched"""
        # make sure account doesn't exist
        await create_account(MockData.discord_id, conn=conn)

        account = await get_account(MockData.discord_id, create=False, conn=conn)
        assert account is not None
