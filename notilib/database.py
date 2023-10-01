"""Main database connector"""


import os
import logging
from typing import Any


import asyncpg

from dotenv import load_dotenv; load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    """Main database connector class that establishes a constant
    connection to the database that is shared throughout the program
    by reusing the same instance of the class."""
    # global class instance
    _instance = None

    conn: asyncpg.Connection = None

    # define values within so that they can be overridden
    host = os.getenv('postgres_host')
    port = os.getenv('postgres_port')
    database = os.getenv('postgres_database')
    user = os.getenv("postgres_user")
    password = os.getenv('postgres_password')

    # make sure only one instance exists
    def __new__(cls) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance


    async def connect(self) -> asyncpg.Connection:
        """
        Connects to the database\\
        This operation is in place, but for convenience sake,\
            the connection is also returned
        :return: the `asyncpg.Connection` object of the connection (self.conn)
        """
        # connect if connection doesnt exist or is closed
        if self.conn is None or self.conn.is_closed():
            try:
                self.conn = await asyncpg.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                logger.info("Connected to PostgreSQL database!")
            except (Exception, asyncpg.PostgresError) as error:
                logger.info(f"Error while connecting to PostgreSQL: {error}")
                return

        return self.conn


    async def close(self):
        """Closes are database connection"""
        if self.conn:
            await self.conn.close()
            logger.info("Disconnected from PostgreSQL database.")


    async def reconnect(self):
        """Re-establishes the connection to the database"""
        await self.close()
        await self.connect()
