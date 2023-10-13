import pytest

from .utils import MockData, execute_in_transaction
from notilib import (
    ConfirmationError,
    create_account,
    delete_account,
    get_account,
    set_account_blacklist
)


class TestAccountCreation:
    @execute_in_transaction
    async def _create_account(self, *args, **kwargs):
        account = await get_account(MockData.discord_id)
        if account:
            await delete_account(MockData.discord_id, confirm=True)

        # create and get account
        await create_account(MockData.discord_id, *args, **kwargs)
        account = await get_account(MockData.discord_id)

        # make sure account exists
        assert account is not None
        return account


    @pytest.mark.asyncio
    async def test_create_account_default(self):
        await self._create_account()

    @pytest.mark.asyncio
    async def test_create_account_permissions(self):
        account = await self._create_account(permissions=['foo', 'bar'])
        assert account.permissions == ['foo', 'bar']

    @pytest.mark.asyncio
    async def test_create_account_blacklisted(self):
        account = await self._create_account(blacklisted=True)
        assert account.blacklisted == 1

    @pytest.mark.asyncio
    async def test_create_account_custom_id(self):
        account = await self._create_account(account_id=123)
        assert account.account_id == 123

    @pytest.mark.asyncio
    async def test_create_account_creation_timestamp(self):
        account = await self._create_account(creation_timestamp=123)
        assert account.creation_timestamp == 123


class TestAccountDeletion:
    @execute_in_transaction
    async def _delete_account(self, confirmation: bool):
        # make sure the account exists
        await create_account(MockData.discord_id)

        # delete the account and make sure it doesnt exist
        await delete_account(MockData.discord_id, confirm=confirmation)

        account = await get_account(MockData.discord_id)
        assert account is None


    @pytest.mark.asyncio
    async def test_delete_account_with_confirmation(self):
        await self._delete_account(confirmation=True)

    @pytest.mark.asyncio
    async def test_delete_account_without_confirmation(self):
        with pytest.raises(ConfirmationError):
            await self._delete_account(confirmation=False)


class TestAccountBlacklisting:
    @execute_in_transaction
    @pytest.mark.asyncio
    async def test_blacklist_account_doesnt_exist_create(self):
        """Test blacklisting an account that doesnt exist with
        the create if account doesn't exist parameter as true"""
        # make sure account doesn't exist
        await delete_account(MockData.discord_id, confirm=True)

        await set_account_blacklist(
            MockData.discord_id, blacklisted=True, create=True)

        account = await get_account(MockData.discord_id)

        assert account is not None
        assert account.blacklisted == 1

    @execute_in_transaction
    @pytest.mark.asyncio
    async def test_blacklist_account_does_exist(self):
        """Test blacklisting an existing account"""
        # make sure account does exist
        await create_account(MockData.discord_id)

        await set_account_blacklist(
            MockData.discord_id, blacklisted=True)

        account = await get_account(MockData.discord_id)

        assert account is not None
        assert account.blacklisted == 1


class TestGetAccount:
    @execute_in_transaction
    @pytest.mark.asyncio
    async def test_get_account_doesnt_exist_do_create(self):
        """Account doesn't exist, account will be created and returned"""
        # make sure account doesn't exist
        await delete_account(MockData.discord_id, confirm=True)

        await get_account(MockData.discord_id, create=True)

        # get account with seperate function call
        account = await get_account(MockData.discord_id)
        assert account is not None

    @execute_in_transaction
    @pytest.mark.asyncio
    async def test_get_account_doesnt_exist_dont_create(self):
        """Account doesn't exist, account will not be created and returned"""
        # make sure account doesn't exist
        await delete_account(MockData.discord_id, confirm=True)

        account = await get_account(MockData.discord_id, create=False)
        assert account is None

    @execute_in_transaction
    @pytest.mark.asyncio
    async def test_get_account_exists_dont_create(self):
        """Account exists, account will be directly fetched"""
        # make sure account doesn't exist
        await create_account(MockData.discord_id)

        account = await get_account(MockData.discord_id, create=False)
        assert account is not None
