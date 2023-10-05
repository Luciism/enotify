"""Main database connector"""


import os
import logging
from functools import wraps
from typing import Any, Coroutine

import asyncpg
from dotenv import load_dotenv; load_dotenv()


logger = logging.getLogger(__name__)


class Database:
    """Main database connector class that establishes a constant
    connection to the database that is shared throughout the program
    by reusing the same instance of the class."""
    # global class instance
    _instance = None

    # custom cleanup callable
    _cleanup = None

    # define values within so that they can be overridden
    host = os.getenv('postgres_host')
    port = os.getenv('postgres_port')
    database = os.getenv('postgres_database')
    user = os.getenv("postgres_user")
    password = os.getenv('postgres_password')

    # make sure only one instance exists (singleton)
    def __new__(cls) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance


    # global connection pool
    pool: asyncpg.pool.Pool = None


    async def _create_pool(self) -> asyncpg.Pool:
        self.pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        return self.pool


    async def connect(self) -> asyncpg.Pool:
        if self.pool is None or self.pool._closed:
            await self._create_pool()
            logger.info("Created new database connection pool.")
        return self.pool


    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Closed the database connection pool.")


    async def reconnect(self):
        """Re-establishes the connection to the database"""
        await self.close()
        await self.connect()


    def on_cleanup(self, func: Coroutine[Any, Any, Any]):
        """
        Add custom code for when the `.cleanup()` method is called
        :param func: the asynchronous function to call in the `.cleanup()` method
        """
        # set custom cleanup callable
        self._cleanup = func
        return func


    async def cleanup(self) -> None:
        """
        Executes cleanup code along with any custom cleanup code set with\
            the `@Database.on_cleanup` decorator
        """
        # run default cleanup
        # currently nothing

        # run custom cleanup if is valid
        if callable(self._cleanup):
            await self._cleanup()


def ensure_connection(func):
    """
    Decorator that ensures a database connection is resolved.
    If the `conn` parameter is `None`, a new connection will be acquired,
    otherwise the passed `conn` parameter connection will be used.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        conn = kwargs.get('conn')
        if conn:  # use provided connection
            return await func(*args, **kwargs)

        pool = await Database().connect()

        async with pool.acquire() as conn:  # otherwise, acquire new connection
            kwargs['conn'] = conn
            return await func(*args, **kwargs)
    return wrapper
