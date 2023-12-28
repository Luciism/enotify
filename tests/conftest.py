import asyncio
import logging

import pytest
import pytest_asyncio
from asyncpg import Connection

from .utils import db, RollbackTransaction

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def conn():
    # pool = await db.connect()
    # async with pool.acquire() as conn:
    #     yield conn

    try:
        pool = await db.connect()
        async with pool.acquire() as conn:
            conn: Connection
            async with conn.transaction():
                yield conn

                # rollback the transaction by raising an error
                raise RollbackTransaction
    except RollbackTransaction:
        # logging.info('rollback transition exception raised and caught')
        pass
