import os

from dotenv import load_dotenv

from helper import Client
from notilib import setup_logging, config, PROJECT_PATH


load_dotenv(f'{PROJECT_PATH}/.env')
setup_logging(
    logs_dir=os.path.join(PROJECT_PATH, 'logs/bot'),
    set_stream_handler=False
)

client = Client(
    cogs=[
        'cogs.gmail',
        'cogs.commands.help'
    ]
)

if __name__ == '__main__':
    client.run(
        token=os.getenv('bot_token'),
        root_logger=True,
        log_level=config('apps.bot.log_level')
    )
