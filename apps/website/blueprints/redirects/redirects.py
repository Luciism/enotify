import logging

from quart import (
    Blueprint,
    redirect
)

from notilib import config


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')


redirects_bp = Blueprint(
    name='redirects',
    import_name=__name__,
)


@redirects_bp.route('/support')
async def support_route():
    return redirect(config('global.links.discord_server'))

@redirects_bp.route('/invite')
async def invite_route():
    return redirect(config('global.links.invite'))
