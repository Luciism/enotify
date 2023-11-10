"""Wraps `notilib.email_addresses` for the `gmail` webmail service"""

from asyncpg import Connection

from ...database import ensure_connection
from ...filters import EmailNotificationFilters
from ... import email_addresses


@ensure_connection
async def get_email_addresses(
    discord_id: int,
    conn: Connection=None
) -> list[str]:
    """
    Returns a list of email addresses associated with the provided discord id
    :param discord_id: the discord id to find the respective email addresses of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    return await email_addresses.get_email_addresses(
        discord_id, webmail_service='gmail', conn=conn)


@ensure_connection
async def email_address_to_discord_ids(
    email_address: str,
    conn: Connection=None
) -> list[int]:
    """
    Returns a list of discord ids that have a certain email tied to them
    :param email_address: the email address to find the respective discord ids of
    :param conn: an open database connection to execute on, if left as `None`,\
        one will be acquired automatically (must be passed as a keyword argument)
    """
    return await email_addresses.email_address_to_discord_ids(
        email_address, webmail_service='gmail', conn=conn)


class GmailEmailAddress:
    def __init__(self, discord_id: int, email_address: str) -> None:
        self.__default = object()

        self.discord_id = discord_id
        self.email_address = email_address

        self._filters = self.__default


    @ensure_connection
    async def add_email_address(self, conn: Connection=None) -> None:
        """
        Adds an email address to an account's list of email addresses
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await email_addresses.add_email_address(
            self.discord_id, self.email_address, webmail_service='gmail', conn=conn)


    @ensure_connection
    async def remove_email_address(self, conn: Connection=None) -> None:
        """
        Removes a specified email address from a user account
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await email_addresses.remove_email_address(
            self.discord_id, self.email_address, webmail_service='gmail', conn=conn)


    @property
    def filters(self) -> EmailNotificationFilters:
        """Email notification filters manager"""
        if self._filters is self.__default:
            self._filters = EmailNotificationFilters(
                self.discord_id, self.email_address, webmail_service='gmail')
        return self._filters
