import logging
from threading import Thread

import discord
from discord.ext import commands

from .socket_listener import start_socket_listener


logger = logging.getLogger(__name__)


# main bot client
class Client(commands.Bot):
    def __init__(self, *, intents: discord.Intents=None, cogs: list[str]=None):
        if intents is None:
            intents = discord.Intents.default()
            intents.members = True

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('$')
        )

        self.cog_list = cogs


    async def setup_hook(self):
        # launch gmail email received socket listener in different thread
        Thread(target=start_socket_listener, args=(self,)).start()

        # load passed cogs
        if self.cog_list is not None:
            for cog in self.cog_list:
                try:
                    await self.load_extension(cog)
                    logger.info(f'Loaded cog: {cog}')
                except (commands.errors.ExtensionNotFound, commands.errors.ExtensionFailed):
                    logger.error(f'Failed to load cog: {cog}')

        # sync slash command tree
        await self.tree.sync()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})\n------')

        await self.change_presence(
            activity=discord.Activity(
                name='beta development',
                type=discord.ActivityType.watching
            )
        )
