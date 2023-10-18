import logging

from quart import (
    Blueprint,

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
    return