import asyncio
import logging

import pytest
import pytest_asyncio
from asyncpg import Connection

from .utils import db, RollbackTransaction
from notilib import PROJECT_PATH


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


def _load_sql_from_file(filename: str):
    with open(f'{PROJECT_PATH}/schema/{filename}') as file:
        return file.read()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def database_schema_setup_and_teardown():
    conn: Connection

    pool = await db.connect()
    async with pool.acquire() as conn:

        # make sure schema doesnt exist beforehand
        await conn.execute('DROP SCHEMA IF EXISTS public CASCADE')
        await conn.execute('CREATE SCHEMA public')

        await conn.execute(_load_sql_from_file('tables.sql'))
        await conn.execute(_load_sql_from_file('functions.sql'))
        await conn.execute(_load_sql_from_file('extensions.sql'))

    yield

    # remove newly created schema
    async with pool.acquire() as conn:
        await conn.execute('DROP SCHEMA public CASCADE')
