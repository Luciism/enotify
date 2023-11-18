import os

from asyncpg import Connection

from .common import WebmailServiceLiteral
from .database import Database, ensure_connection


class EmailNotificationFilters:
    def __init__(
        self,
        discord_id: int,
        email_address: str,
        webmail_service: WebmailServiceLiteral
    ) -> None:
        self.__default = object()

        self.discord_id = discord_id
        self.email_address = email_address
        self.webmail_service = webmail_service

        self._refresh()


    def _refresh(self) -> None:
        self._sender_whitelist_enabled: bool = self.__default
        self._whitelisted_senders: list[str] = self.__default


    async def __load_filter_data(self) -> None:
        pool = await Database().connect()

        async with pool.acquire() as conn:
            conn: Connection

            data = await conn.fetchrow(
                'SELECT sender_whitelist_enabled, decrypt_array(whitelisted_senders, $4) '
                'AS whitelisted_senders FROM email_notification_filters WHERE discord_id = $1 '
                'AND pgp_sym_decrypt(email_address, $4) = $2 AND webmail_service = $3',
                self.discord_id, self.email_address, self.webmail_service,
                os.getenv('database_encryption_key')
            )

            if data is not None:
                self._sender_whitelist_enabled = data['sender_whitelist_enabled']
                self._whitelisted_senders = data['whitelisted_senders'] or []

                return

            # default values
            self._sender_whitelist_enabled = False
            self._whitelisted_senders = []


    @property
    async def sender_whitelist_enabled(self) -> bool:
        """Whether or not sender whitelisting is enabled"""
        if self._sender_whitelist_enabled is self.__default:
            await self.__load_filter_data()
        return self._sender_whitelist_enabled


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


    @property
    async def whitelisted_senders(self) -> list:
        """A list of senders that are whitelisted"""
        if self._whitelisted_senders is self.__default:
            await self.__load_filter_data()
        return self._whitelisted_senders


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
        sender_email_address = sender_email_address.lower()

        # sender is already whitelisted
        if sender_email_address in await self.whitelisted_senders:
            return False

        await conn.execute(
            'UPDATE email_notification_filters '
            'SET whitelisted_senders = whitelisted_senders || pgp_sym_encrypt($1, $5) '
            'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $5) = $3 '
            'AND webmail_service = $4', sender_email_address, self.discord_id,
            self.email_address, self.webmail_service, os.getenv('database_encryption_key')
        )

        return True


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
        await conn.execute(
            'UPDATE email_notification_filters SET whitelisted_senders = '
            'remove_encrypted_array_element($1, whitelisted_senders, $5) '
            'WHERE discord_id = $2 AND pgp_sym_decrypt(email_address, $5) = $3 '
            'AND webmail_service = $4', sender_email_address.lower(), self.discord_id,
            self.email_address, self.webmail_service, os.getenv('database_encryption_key')
        )
