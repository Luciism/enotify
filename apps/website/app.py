import os
import logging

from quart import Quart
from dotenv import load_dotenv; load_dotenv()

from notilib import Database, setup_logging, PROJECT_PATH

from blueprints.gmail.gmail import gmail_bp
from blueprints.discord.discord import discord_bp
from blueprints.dashboard.dashboard import dashboard_bp


# -------------------------- LOGGING -------------------------- #
setup_logging(os.path.join(PROJECT_PATH, 'logs/website'))
logger = logging.getLogger(__name__)


# ---------------------------- APP ---------------------------- #
app = Quart(__name__)
app.config['SECRET_KEY'] = os.getenv('flask_secret_key')
app.config['EXPLAIN_TEMPLATE_LOADING'] = None

app.register_blueprint(gmail_bp)
app.register_blueprint(discord_bp)
app.register_blueprint(dashboard_bp)

# -------------------------- DATABASE -------------------------- #
db = Database()

@app.before_serving
async def create_db_pool():
    await db._create_pool()


@app.after_serving
async def close_db_pool():
    await db.pool.close()
    db.pool.terminate()


# ---------------------------- RUN ---------------------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000)
