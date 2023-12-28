import logging

from quart import (
    Blueprint,
    render_template
)

from helper import default_page_context_data


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')


login_bp = Blueprint(
    name='login',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/login/'
)


@login_bp.route('/login')
async def login_route():
    return await render_template(
        'login.html', data=await default_page_context_data())
