from os import getenv
from dotenv import load_dotenv

from helper import Client
from notilib import setup_logging, PROJECT_PATH


if __name__ == '__main__':
    load_dotenv(f'{PROJECT_PATH}/.env')
    setup_logging()

    Client().run(getenv('bot_token'), root_logger=True)
