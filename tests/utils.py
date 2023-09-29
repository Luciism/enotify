from functools import wraps

from notilib import Database


class RollbackTransaction(Exception):
    """Raised in order to rollback transactions"""

# setup database class to use test database
db = Database()
db.database = 'enotify_test'


def execute_in_transaction(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        await db.connect()

        try:
            async with db.conn.transaction():
                # execute coroutine in transaction
                result = await coro(*args, **kwargs)

                # rollback the transaction by raising an error
                raise RollbackTransaction
        except RollbackTransaction:
            return result

    return wrapper


class MockData:
    discord_id: int = 774848780234653726