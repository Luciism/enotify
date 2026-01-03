import pytest

from .utils import MockData, add_mock_email_address
from notilib import EmailNotificationFilters


@pytest.fixture
def filters(request: pytest.FixtureRequest):
    _filters = EmailNotificationFilters(
        discord_id=MockData.discord_id,
        email_address=MockData.email_address.random(),
        webmail_service=MockData.webmail_service
    )

    # set connection that the class will use for @property methods
    _filters._conn = request.getfixturevalue('conn')

    # prevents @property methods from loading only once
    _filters._loading = 'strict'

    return _filters


@pytest.mark.asyncio
async def test_add_whitelisted_sender(conn, filters: EmailNotificationFilters):
    await add_mock_email_address(filters.email_address, conn=conn)

    await filters.add_whitelisted_sender(MockData.email_address[1], conn=conn)
    assert MockData.email_address[1].lower() in await filters.whitelisted_senders


@pytest.mark.asyncio
async def test_remove_whitelisted_sender(conn, filters: EmailNotificationFilters):
    await add_mock_email_address(filters.email_address, conn=conn)

    await filters.add_whitelisted_sender(MockData.email_address[1], conn=conn)
    await filters.remove_whitelisted_sender(MockData.email_address[1], conn=conn)

    assert MockData.email_address[1].lower() \
        not in await filters.whitelisted_senders


@pytest.mark.asyncio
async def test_add_blacklisted_sender(conn, filters: EmailNotificationFilters):
    await add_mock_email_address(filters.email_address, conn=conn)

    await filters.add_blacklisted_sender(MockData.email_address[1], conn=conn)
    assert MockData.email_address[1].lower() in await filters.blacklisted_senders


@pytest.mark.asyncio
async def test_remove_blacklisted_sender(conn, filters: EmailNotificationFilters):
    await add_mock_email_address(filters.email_address, conn=conn)

    await filters.add_blacklisted_sender(MockData.email_address[1], conn=conn)
    await filters.remove_blacklisted_sender(MockData.email_address[1], conn=conn)

    assert MockData.email_address[1].lower() \
        not in await filters.blacklisted_senders


@pytest.mark.asyncio
async def test_set_sender_whitelist_enabled(conn, filters: EmailNotificationFilters):
    await add_mock_email_address(filters.email_address, conn=conn)

    await filters.set_sender_whitelist_enabled(enabled=True, conn=conn)
    assert await filters.sender_whitelist_enabled == True
