import os
import logging

from flask import Flask
from dotenv import load_dotenv; load_dotenv()

from notilib import setup_logging, Database

from blueprints.gmail.gmail import gmail_bp
from blueprints.discord.discord import discord_bp


# -------------------------- LOGGING -------------------------- #
setup_logging()
logger = logging.getLogger('enotify.apps.website')


# -------------------------- DATABASE -------------------------- #
db = Database()

# set cleanup code to close the connection on cleanup
@db.on_cleanup
async def on_cleanup():
    if db._pool:
        db._pool.terminate()

# ---------------------------- APP ---------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('flask_secret_key')

app.register_blueprint(gmail_bp)
app.register_blueprint(discord_bp)


# ---------------------------- MISC --------------------------- #
@app.route('/test-pub-sub', methods=['GET', 'POST'])
def test_pub_sub(): return {'success': True}


# ---------------------------- RUN ---------------------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0")
