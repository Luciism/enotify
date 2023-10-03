from asyncpg import Pool
from quart import Quart


class QuartClient(Quart):
    db_pool: Pool
