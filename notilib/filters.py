import os
from typing import Literal

from asyncpg import Connection

from .common import WebmailServiceLiteral
from .database import ensure_connection


class EmailNotificationFilters:
    def __init__(
        self,
        discord_id: int,
        email_address: str,
        webmail_service: WebmailServiceLiteral
    ) -> None:
        self.__default = object()
        self._conn = None
        self._loading: str = 'lazy'

        self.discord_id = discord_id
        self.email_address = email_address
        self.webmail_service = webmail_service

        self._refresh()


    def _refresh(self) -> None:
        self._sender_whitelist_enabled: bool = self.__default
        self._whitelisted_senders: list[str] = self.__default
        self._blacklisted_senders: list[str] = self.__default


    @ensure_connection
    async def __load_filter_data(self, conn: Connection=None) -> None:
        data = await conn.fetchrow(
            'SELECT sender_whitelist_enabled, decrypt_array(whitelisted_senders, $4) '
            'AS whitelisted_senders, decrypt_array(blacklisted_senders, $4) '
            'AS blacklisted_senders FROM email_notification_filters WHERE discord_id = $1 '
            'AND pgp_sym_decrypt(email_address, $4) = $2 AND webmail_service = $3',
            self.discord_id, self.email_address, self.webmail_service,
            os.getenv('database_encryption_key')
        )

        if data is not None:
            self._sender_whitelist_enabled = data['sender_whitelist_enabled']
            self._whitelisted_senders = data['whitelisted_senders'] or []
            self._blacklisted_senders = data['blacklisted_senders'] or []

            return

        # default values
        self._sender_whitelist_enabled = False
        self._whitelisted_senders = []
        self._blacklisted_senders = []


    @property
    async def sender_whitelist_enabled(self) -> bool:
        """Whether or not sender whitelisting is enabled"""
        if self._sender_whitelist_enabled is self.__default or self._loading != 'lazy':
            await self.__load_filter_data(conn=self._conn)
        return self._sender_whitelist_enabled


    @property
    async def whitelisted_senders(self) -> list:
        """A list of senders that are whitelisted"""
        if self._whitelisted_senders is self.__default or self._loading != 'lazy':
            await self.__load_filter_data(conn=self._conn)
        return self._whitelisted_senders


    @property
    async def blacklisted_senders(self) -> list:
        """A list of senders that are blacklisted"""
        if self._blacklisted_senders is self.__default or self._loading != 'lazy':
            await self.__load_filter_data(conn=self._conn)
        return self._blacklisted_senders


    @ensure_connection
    async def set_sender_whitelist_enabled(
        self,
        enabled: bool,
        conn: Connection=None
    ) -> None:
        """
        Sets whether or not sender whitelisting is enabled
        :param enabled: whether to set sender whitelist to enabled or disabled
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        enabled = bool(enabled)
        self._sender_whitelist_enabled = enabled

        # set sender whitelist enabled value in database
        await conn.execute(
            'UPDATE email_notification_filters SET sender_whitelist_enabled = $1 '
            'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $5) = $3 '
            'AND webmail_service = $4', enabled, self.discord_id,
            self.email_address, self.webmail_service, os.getenv('database_encryption_key')
        )


    async def __add_sender(
        self,
        sender_email_address: str,
        conn: Connection,
        target: Literal['whitelist', 'blacklist']
    ) -> bool:
        # 'whitelisted_senders' || 'blacklisted_senders'
        target_full = f'{target}ed_senders'

        sender_email_address = sender_email_address.lower()

        # check if sender is already whitelisted / blacklisted
        if sender_email_address in await getattr(self, target_full):
            return False

        await conn.execute(
            'UPDATE email_notification_filters '
            f'SET {target_full} = {target_full} || pgp_sym_encrypt($1, $5) '
            'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $5) = $3 '
            'AND webmail_service = $4', sender_email_address, self.discord_id,
            self.email_address, self.webmail_service, os.getenv('database_encryption_key')
        )

        return True


    async def __remove_sender(
        self,
        sender_email_address: str,
        conn: Connection,
        target: Literal['whitelist', 'blacklist']
    ) -> None:
        await conn.execute(
            f'UPDATE email_notification_filters SET {target}ed_senders = '
            f'remove_encrypted_array_element($1, {target}ed_senders, $5) '
            'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $5) = $3 '
            'AND webmail_service = $4', sender_email_address.lower(), self.discord_id,
            self.email_address, self.webmail_service, os.getenv('database_encryption_key')
        )



    @ensure_connection
    async def add_whitelisted_sender(
        self,
        sender_email_address: str,
        conn: Connection=None
    ) -> bool:
        """
        Adds a sender to the sender whitelist
        :param sender_email_address: the email address of the sender to whitelist
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        :return bool: whether the sender was already whitelisted or not
        """
        return await self.__add_sender(sender_email_address, conn, target='whitelist')


    @ensure_connection
    async def remove_whitelisted_sender(
        self,
        sender_email_address: str,
        conn: Connection=None
    ) -> None:
        """
        Removes a sender from the sender whitelist
        :param sender_email_address: the email address of the sender to remove\
            from the whitelist
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await self.__remove_sender(sender_email_address, conn, 'whitelist')


    @ensure_connection
    async def add_blacklisted_sender(
        self,
        sender_email_address: str,
        conn: Connection=None
    ) -> bool:
        """
        Adds a sender to the sender blacklist
        :param sender_email_address: the email address of the sender to blacklist
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        :return bool: whether the sender was already blacklisted or not
        """
        return await self.__add_sender(sender_email_address, conn, target='blacklist')


    @ensure_connection
    async def remove_blacklisted_sender(
        self,
        sender_email_address: str,
        conn: Connection=None
    ) -> None:
        """
        Removes a sender from the sender blacklist
        :param sender_email_address: the email address of the sender to remove\
            from the blacklist
        :param conn: an open database connection to execute on, if left as `None`,\
            one will be acquired automatically (must be passed as a keyword argument)
        """
        await self.__remove_sender(sender_email_address, conn, 'blacklist')
