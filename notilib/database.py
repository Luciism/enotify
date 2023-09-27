import os
import asyncpg
from typing import Any

from dotenv import load_dotenv; load_dotenv()


class Database:
    # make sure only one instance exists
    _instance = None


    def __new__(cls) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance


    def __init__(self):
        self.host = os.getenv('postgres_host')
        self.port = os.getenv('postgres_port')
        self.database = os.getenv('postgres_database')
        self.user = os.getenv("postgres_user")
        self.password = os.getenv('postgres_password')
        self.conn: asyncpg.Connection = None


    async def connect(self):
        try:
            self.conn = await asyncpg.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Connected to PostgreSQL database!")
        except (Exception, asyncpg.PostgresError) as error:
            print(f"Error while connecting to PostgreSQL: {error}")


    async def close(self):
        if self.conn:
            await self.conn.close()
            print("Disconnected from PostgreSQL database.")


"""TEST"""

import asyncio

async def main():
    db = Database()
    await db.connect()

    # await db.conn.execute()

asyncio.run(main())
