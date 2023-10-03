"""Main database connector"""


import os
import logging
from asyncio import AbstractEventLoop
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
    def __new__(cls, *args, **kwargs) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance


    # global connection pool
    _pool: asyncpg.pool.Pool = None


    async def _create_pool(self, loop: AbstractEventLoop=None) -> asyncpg.Pool:
        self._pool = await asyncpg.create_pool(
            loop=loop,

            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        return self._pool


    async def connect(self) -> asyncpg.Connection:
        if self._pool is None or self._pool._closed:
            await self._create_pool()
            logger.info("Connected to PostgreSQL database!")
        return self._pool.acquire(timeout=5)


    async def close(self):
        if self._pool:
            await self._pool.close()
            logger.info("Disconnected from PostgreSQL database.")


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
