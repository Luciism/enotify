import os

import discord
from dotenv import load_dotenv

from helper import Client
from notilib import setup_logging, PROJECT_PATH


load_dotenv(f'{PROJECT_PATH}/.env')
setup_logging(
    logs_dir=os.path.join(PROJECT_PATH, 'logs/bot'),
    set_stream_handler=False
)


client = Client()

@client.event
async def on_gmail_email_recieve(*args):
    channel = client.get_channel(1158740124708901015)

    await channel.send('email recieved event test')
    print(args)


@client.tree.command(name='test', description='test')
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('test motrher cukcer!')


if __name__ == '__main__':
    client.run(os.getenv('bot_token'), root_logger=True)
