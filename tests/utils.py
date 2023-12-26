import random
from functools import wraps
from typing import Literal

from asyncpg import Connection

from notilib import Database, email_addresses


class RollbackTransaction(Exception):
    """Raised in order to rollback transactions"""

# setup database class to use test database
db = Database()
db.database = 'enotify_test'


def execute_in_transaction(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            pool = await db.connect()
            async with pool.acquire() as conn:
                conn: Connection
                async with conn.transaction():
                    # execute coroutine in transaction
                    result = await coro(*args, **kwargs)

                    # rollback the transaction by raising an error
                    raise RollbackTransaction
        except RollbackTransaction:
            return result

    return wrapper


class _EmailAddress:
    all = [
        'Prudence.Stroman60@gmail.com',
        'Lily.Ondricka71@gmail.com',
        'Joanny_Treutel@yahoo.com',
        'Barry95@hotmail.com',
        'Kendall.Frami15@hotmail.com',
        'Ariane.Kris@yahoo.com',
        'Melody.Lockman84@gmail.com',
        'Michele.Hayes71@yahoo.com',
        'Layne_Funk@gmail.com',
        'Cornelius84@hotmail.com',
        'Warren73@hotmail.com',
        'Lynn.Schneider@hotmail.com',
        'Brandy_Nicolas@hotmail.com',
        'Lisandro.Runolfsdottir@hotmail.com',
        'Alberto18#amazon@yahoo.com',
        'Markus.Pollich@gmail.com'
    ]

    def __call__(self) -> str:
        return self.all[0]

    def __str__(self) -> str:
        return self.all[0]

    def __getitem__(self, index: int) -> str:
        return self.all[index]

    def random(self) -> str:
        return random.choice(self.all)



class MockData:
    encryption_key: str = '28b784785df7b4a6cd557cf1d620f231'

    email_address = _EmailAddress()

    discord_id: Literal[774848780234653726] = 774848780234653726
    discord_id_2: Literal[453212491884885163] = 453212491884885163
    discord_id_3: Literal[582136343667726502] = 582136343667726502
    discord_id_3: Literal[363502852571134156] = 363502852571134156

    webmail_service: Literal['gmail'] = 'gmail'
    webmail_service_2: Literal['yahoo'] = 'yahoo'
    webmail_service_3: Literal['outlook'] = 'outlook'
    webmail_service_4: Literal['hotmail'] = 'hotmail'


async def _add_email_address(
    email_address: str,
    webmail_service: str=MockData.webmail_service,
    discord_id: int=MockData.discord_id
) -> None:
    await email_addresses.add_email_address(
        discord_id=discord_id,
        email_address=email_address,
        webmail_service=webmail_service
    )
