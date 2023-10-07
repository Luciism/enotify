import logging

import discord
from discord.ext import commands

from notilib import Database


logger = logging.getLogger('enotify')


# main bot client
class Client(commands.Bot):
    def __init__(self, *, intents: discord.Intents=None):
        if intents is None:
            intents = discord.Intents.default()

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('$')
        )

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})\n------')

        await self.change_presence(
            activity=discord.Activity(
                name='beta development',
                type=discord.ActivityType.watching
            )
        )
