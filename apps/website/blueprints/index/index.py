from quart import (
    Blueprint,
    render_template
)

from helper import default_page_context_data, root_logger


index_bp = Blueprint(
    name='index',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/index/'
)

@index_bp.before_app_serving
def before_app_serving():
    root_logger.info(f'Blueprint registered: {__name__}')


@index_bp.route('/')
@index_bp.route('/home')
async def index_route():
    return await render_template(
        'index.html', data=await default_page_context_data())
