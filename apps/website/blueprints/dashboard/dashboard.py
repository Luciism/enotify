import logging

from quart import (
    Blueprint,
    render_template
)


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')


dashboard_bp = Blueprint(
    name='dashboard',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/'
)


@dashboard_bp.route('/dashboard')
async def dashboard_route():
    data = {
        'user': {
            'avatar_url': 'https://cdn.discordapp.com/avatars/774848780234653726/f7cc9f66438939ae3be14490e205e7d9.webp',
        }
    }

    return await render_template('dashboard.html', data=data)
