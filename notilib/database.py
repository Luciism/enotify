"""Main database connector"""


import os
import asyncpg
from typing import Any

from dotenv import load_dotenv; load_dotenv()


class Database:
    _instance = None
    conn: asyncpg.Connection = None


    # make sure only one instance exists
    def __new__(cls) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance


    async def connect(self) -> asyncpg.Connection:
        """
        Connects to the database
        :return: the `asyncpg.Connection` object of the connection (self.conn)
        """
        # connect if connection doesnt exist or is closed
        if self.conn is None or self.conn.is_closed():
            try:
                self.conn = await asyncpg.connect(
                    host=os.getenv('postgres_host'),
                    port=os.getenv('postgres_port'),
                    database=os.getenv('postgres_database'),
                    user=os.getenv("postgres_user"),
                    password=os.getenv('postgres_password')
                )
                print("Connected to PostgreSQL database!")
            except (Exception, asyncpg.PostgresError) as error:
                print(f"Error while connecting to PostgreSQL: {error}")
                return

        return self.conn


    async def close(self):
        """Closes are database connection"""
        if self.conn:
            await self.conn.close()
            print("Disconnected from PostgreSQL database.")
