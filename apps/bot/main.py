import asyncio
import os
from threading import Thread

import discord
from discord import app_commands
from dotenv import load_dotenv

from helper import Client, start_gmail_listener
from notilib import setup_logging, PROJECT_PATH


load_dotenv(f'{PROJECT_PATH}/.env')
setup_logging(
    logs_dir=os.path.join(PROJECT_PATH, 'logs/bot'),
    set_stream_handler=False
)


client = Client()

# launch gmail email recieved socket listener in different thread
queue = asyncio.Queue()
Thread(target=start_gmail_listener, args=(client, queue)).start()

@client.event
async def on_gmail_email_recieve(args):
    print(args)


@app_commands.command(name='test', description='test')
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('test motrher cukcer!')


if __name__ == '__main__':
    client.run(os.getenv('bot_token'), root_logger=True)
