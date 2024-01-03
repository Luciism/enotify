import os

import discord
from discord import app_commands
from discord.ext import commands

from helper import Client


help_embed = discord.Embed.from_dict({
    "title": "Enotify Help Menu",
    "color": 0x2b2d31,
    "fields": [
        {
            "name": "Links",
            "value": f"• [Website]({os.getenv('base_url')}/)\n• [Documentation](https://enotify-docs.lucism.dev/)"
        }
    ],
    "thumbnail": {
        "url": f"{os.getenv('base_url')}/static/assets/branding/docs-logo.png"
    }
})


class HelpView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label='Get Started',
                style=discord.ButtonStyle.url,
                url='https://enotify-docs.lucism.dev/'
            )
        )

        self.add_item(
            discord.ui.Button(
                label='Dashboard',
                style=discord.ButtonStyle.url,
                url='https://enotify.lucism.dev/dashboard'
            )
        )


class HelpCommandsCog(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    @app_commands.command(name="help", description="Enotify's help menu")
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=help_embed, view=HelpView())


async def setup(client: Client) -> None:
    await client.add_cog(HelpCommandsCog(client))
