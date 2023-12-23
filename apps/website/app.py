import os
import logging

from quart import Quart, render_template
from dotenv import load_dotenv; load_dotenv()

from notilib import Database, setup_logging, PROJECT_PATH
from helper import (
    InvalidDiscordAccessTokenError,
    UserNotLoggedInError,
    response_msg,
    default_page_context_data
)

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


try:
    from dev_endpoints import dev_endpoints_bp
    app.register_blueprint(dev_endpoints_bp)
except ImportError:
    pass

# -------------------------- DATABASE -------------------------- #
db = Database()

@app.before_serving
async def create_db_pool():
    await db._create_pool()


@app.after_serving
async def close_db_pool():
    await db.pool.close()
    db.pool.terminate()


# --------------------------- ERRORS -------------------------- #
@app.errorhandler(404)
async def not_found(error) -> str:
    return await render_template("404.html", data=await default_page_context_data())

@app.errorhandler(InvalidDiscordAccessTokenError)
async def invalid_discord_access_token_error_handler(error) -> dict:
    return response_msg('invalid_discord_access_token')

@app.errorhandler(UserNotLoggedInError)
async def user_not_logged_in_error_handler(error) -> dict:
    return response_msg('not_logged_in')

# ---------------------------- RUN ---------------------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000)
