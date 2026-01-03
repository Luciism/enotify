import asyncio

import pytest
import pytest_asyncio
from asyncpg import Connection

from .utils import db, RollbackTransaction
from notilib import PROJECT_PATH


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


@pytest_asyncio.fixture(scope='session', autouse=True)
async def database_schema_setup_and_teardown():
    conn: Connection

    pool = await db.connect()
    async with pool.acquire() as conn:

        # make sure schema doesnt exist beforehand
        await conn.execute('DROP SCHEMA IF EXISTS public CASCADE')
        await conn.execute('CREATE SCHEMA public')

        await db.setup_schema(conn=conn)

    yield

    # remove newly created schema
    async with pool.acquire() as conn:
        await conn.execute('DROP SCHEMA public CASCADE')
