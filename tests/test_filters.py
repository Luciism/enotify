import pytest

from .utils import MockData, execute_in_transaction, _add_email_address

from notilib import EmailNotificationFilters


filters = EmailNotificationFilters(
    discord_id=MockData.discord_id,
    email_address=MockData.email_address[0],
    webmail_service=MockData.webmail_service
)


@pytest.mark.asyncio
@execute_in_transaction
async def test_add_whitelisted_sender():
    await _add_email_address(MockData.email_address[0])

    await filters.add_whitelisted_sender(MockData.email_address[1])

    filters._refresh()  # make sure lazy `@property` methods are refreshed
    assert MockData.email_address[1].lower() in await filters.whitelisted_senders


@pytest.mark.asyncio
@execute_in_transaction
async def test_remove_whitelisted_sender():
    await _add_email_address(MockData.email_address[0])

    await filters.add_whitelisted_sender(MockData.email_address[1])
    await filters.remove_whitelisted_sender(MockData.email_address[1])

    filters._refresh()
    assert MockData.email_address[1].lower() \
        not in await filters.whitelisted_senders


@pytest.mark.asyncio
@execute_in_transaction
async def test_add_blacklisted_sender():
    await _add_email_address(MockData.email_address[0])

    await filters.add_blacklisted_sender(MockData.email_address[1])

    filters._refresh()
    assert MockData.email_address[1].lower() in await filters.blacklisted_senders


@pytest.mark.asyncio
@execute_in_transaction
async def test_remove_blacklisted_sender():
    await _add_email_address(MockData.email_address[0])

    await filters.add_blacklisted_sender(MockData.email_address[1])
    await filters.remove_blacklisted_sender(MockData.email_address[1])

    filters._refresh()
    assert MockData.email_address[1].lower() \
        not in await filters.blacklisted_senders


@pytest.mark.asyncio
@execute_in_transaction
async def test_set_sender_whitelist_enabled():
    await _add_email_address(MockData.email_address[0])

    await filters.set_sender_whitelist_enabled(enabled=True)

    filters._refresh()
    assert await filters.sender_whitelist_enabled == True
