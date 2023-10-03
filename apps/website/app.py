import os
import logging

from quart import Quart
from dotenv import load_dotenv; load_dotenv()

from notilib import setup_logging, Database
from helper import QuartClient

from blueprints.gmail.gmail import gmail_bp
from blueprints.discord.discord import discord_bp


# -------------------------- LOGGING -------------------------- #
setup_logging()
logger = logging.getLogger('enotify.apps.website')


# ---------------------------- APP ---------------------------- #
app = QuartClient(__name__)
app.config['SECRET_KEY'] = os.getenv('flask_secret_key')

app.register_blueprint(gmail_bp)
app.register_blueprint(discord_bp)

# -------------------------- DATABASE -------------------------- #
db = Database()

@app.before_serving
async def create_db_pool():
    await db._create_pool()


@app.after_serving
async def close_db_pool():
    await db.pool.close()
    db.pool.terminate()


# ---------------------------- MISC --------------------------- #
@app.route('/test-pub-sub', methods=['GET', 'POST'])
async def test_pub_sub(): return {'success': True}


# ---------------------------- RUN ---------------------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
