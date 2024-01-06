from quart import (
    Blueprint,
    redirect
)

from notilib import config
from helper import root_logger


redirects_bp = Blueprint(
    name='redirects',
    import_name=__name__,
)

@redirects_bp.before_app_serving
def before_app_serving():
    root_logger.info(f'Blueprint registered: {__name__}')


@redirects_bp.route('/support')
async def support_route():
    return redirect(config('global.links.discord_server'))

@redirects_bp.route('/invite')
async def invite_route():
    return redirect(config('global.links.invite'))
