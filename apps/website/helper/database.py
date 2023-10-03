import asyncpg
from quart import Quart, g as quart_g
from notilib import Database


class QuartDatabase(Database):
    def __init__(self, app: Quart=None):
        self.app = app

        if app is not None:
            self.init_app(app)


    def init_app(self, app: Quart):
        app.teardown_appcontext(self.teardown)


    async def connect(self) -> asyncpg.Connection:
        print(quart_g)
        if not 'pool' in quart_g:
            print('creating pool')
            quart_g.pool = await self._create_pool()
        return quart_g.pool.acquire(timeout=5)


    async def teardown(self, exception=None):
        print('tearing down connection')
        pool: asyncpg.Pool = quart_g.pop('pool', None)
        print(pool.get_size())

        if pool is not None:
            await pool.close()
            print('tore down connection')
            print(pool.get_size())
