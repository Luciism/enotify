import os

from dotenv import load_dotenv

from helper import Client
from notilib import setup_logging, PROJECT_PATH


load_dotenv(f'{PROJECT_PATH}/.env')
setup_logging(
    logs_dir=os.path.join(PROJECT_PATH, 'logs/bot'),
    set_stream_handler=False
)

client = Client(
    cogs=[
        'cogs.gmail'
    ]
)

if __name__ == '__main__':
    client.run(os.getenv('bot_token'), root_logger=True, log_level=10)
