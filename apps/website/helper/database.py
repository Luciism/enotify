import asyncpg
from flask import Flask, g as flask_g

from notilib import Database


class FlaskDatabase(Database):
    def __init__(self, app: Flask=None):
        self.app = app

        if app is not None:
            self.init_app(app)


    def init_app(self, app: Flask):
        app.teardown_appcontext(self.teardown)


    async def connect(self) -> asyncpg.Connection:
        print(flask_g)
        if not 'pool' in flask_g:
            print('creating pool')
            flask_g.pool = await self._create_pool()
        return flask_g.pool.acquire(timeout=5)


    async def teardown(self, exception=None):
        print('tearing down connection')
        pool: asyncpg.Pool = flask_g.pop('pool', None)
        print(pool.get_size())

        if pool is not None:
            await pool.close()
            print('tore down connection')
            print(pool.get_size())
