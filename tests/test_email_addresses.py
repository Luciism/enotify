import pytest

from .utils import MockData, _add_email_address
from notilib import email_addresses


async def _remove_email_address(email_address: str, conn):
    await email_addresses.remove_email_address(
        discord_id=MockData.discord_id,
        email_address=email_address,
        webmail_service=MockData.webmail_service,
        conn=conn
    )

@pytest.mark.asyncio
async def test_add_email_address(conn):
    await _add_email_address(MockData.email_address(), conn=conn)

    assert MockData.email_address() in await email_addresses.get_email_addresses(
        discord_id=MockData.discord_id,
        webmail_service=MockData.webmail_service,
        conn=conn
    )


@pytest.mark.asyncio
async def test_remove_email_address(conn):
    await _add_email_address(MockData.email_address(), conn=conn)
    await _remove_email_address(MockData.email_address(), conn=conn)

    # make sure email address was removed properly
    assert MockData.email_address() not in await email_addresses.get_email_addresses(
        discord_id=MockData.discord_id,
        webmail_service=MockData.webmail_service,
        conn=conn
    )


@pytest.mark.asyncio
async def test_get_all_email_addresses(conn):
    # add 2 different email addresses
    # TODO: use 2 different webmail services when capacity is added
    await _add_email_address(MockData.email_address[0], conn=conn)
    await _add_email_address(MockData.email_address[1], conn=conn)

    # get both email addresses by discord id
    all_email_addresses_data = await email_addresses.get_all_email_addresses(
        discord_id=MockData.discord_id,
        conn=conn
    )

    all_email_addresses = [
        email_addr_data['email_address']
        for email_addr_data in all_email_addresses_data
    ]

    assert MockData.email_address[0] in all_email_addresses
    assert MockData.email_address[1] in all_email_addresses


@pytest.mark.asyncio
async def test_email_address_to_discord_ids(conn):
    # add same email address under 2 different discord ids
    await _add_email_address(
        MockData.email_address[0],
        webmail_service=MockData.webmail_service,
        discord_id=MockData.discord_id,
        conn=conn
    )
    await _add_email_address(
        MockData.email_address[0],
        webmail_service=MockData.webmail_service,
        discord_id=MockData.discord_id_2,
        conn=conn
    )

    # get both discord ids by email address
    discord_ids = await email_addresses.email_address_to_discord_ids(
        email_address=MockData.email_address[0],
        webmail_service=MockData.webmail_service,
        conn=conn
    )
    assert MockData.discord_id in discord_ids
    assert MockData.discord_id_2 in discord_ids
