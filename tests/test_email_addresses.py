import pytest

from .utils import MockData, execute_in_transaction, _add_email_address

from notilib import email_addresses


async def _remove_email_address(email_address: str):
    await email_addresses.remove_email_address(
        discord_id=MockData.discord_id,
        email_address=email_address,
        webmail_service=MockData.webmail_service
    )

@pytest.mark.asyncio
@execute_in_transaction
async def test_add_email_address():
    await _add_email_address(MockData.email_address())

    assert MockData.email_address() in await email_addresses.get_email_addresses(
        discord_id=MockData.discord_id,
        webmail_service=MockData.webmail_service
    )


@pytest.mark.asyncio
@execute_in_transaction
async def test_remove_email_address():
    await _add_email_address(MockData.email_address())
    await _remove_email_address(MockData.email_address())

    # make sure email address was removed properly
    assert MockData.email_address() not in await email_addresses.get_email_addresses(
        discord_id=MockData.discord_id,
        webmail_service=MockData.webmail_service
    )


@pytest.mark.asyncio
@execute_in_transaction
async def test_get_all_email_addresses():
    # add 2 different email addresses
    # TODO: use 2 different webmail services when capacity is added
    await _add_email_address(MockData.email_address[0])
    await _add_email_address(MockData.email_address[1])

    # get both email addresses by discord id
    all_email_addresses_data = await email_addresses.get_all_email_addresses(
        discord_id=MockData.discord_id,
    )

    all_email_addresses = [
        email_addr_data['email_address']
        for email_addr_data in all_email_addresses_data
    ]

    assert MockData.email_address[0] in all_email_addresses
    assert MockData.email_address[1] in all_email_addresses


@pytest.mark.asyncio
@execute_in_transaction
async def test_email_address_to_discord_ids():
    # add same email address under 2 different discord ids
    await _add_email_address(
        MockData.email_address[0],
        webmail_service=MockData.webmail_service,
        discord_id=MockData.discord_id
    )
    await _add_email_address(
        MockData.email_address[0],
        webmail_service=MockData.webmail_service,
        discord_id=MockData.discord_id_2
    )

    # get both discord ids by email address
    discord_ids = await email_addresses.email_address_to_discord_ids(
        email_address=MockData.email_address[0],
        webmail_service=MockData.webmail_service
    )
    assert MockData.discord_id in discord_ids
    assert MockData.discord_id_2 in discord_ids
