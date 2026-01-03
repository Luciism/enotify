from quart import Blueprint, render_template, redirect

from helper import (
    InvalidDiscordAccessTokenError,
    UserNotLoggedInError,
    response_msg,
    default_page_context_data,
    request,
    root_logger
)


error_handling_bp = Blueprint(
    name='error_handling',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/error_handling/'
)

@error_handling_bp.before_app_serving
def before_app_serving():
    root_logger.info(f'Blueprint registered: {__name__}')


@error_handling_bp.route('/error/<string:error>')
async def error_msg_route(error: str):
    res_msg = response_msg(error)

    default_page_data = await default_page_context_data()

    # not a valid error message
    if res_msg['message'] == error:
        return await render_template("404.html", data=default_page_data)

    return await render_template('something_went_wrong.html', data={
        **default_page_data,
        'text': {
            'title': res_msg['message'],
            'description': res_msg['description'],
        }
    })


# ------------------------- EXCEPTIONS ------------------------ #
@error_handling_bp.app_errorhandler(InvalidDiscordAccessTokenError)
async def invalid_discord_access_token_error_handler(error) -> dict:
    return response_msg('invalid_discord_access_token')


@error_handling_bp.app_errorhandler(UserNotLoggedInError)
async def user_not_logged_in_error_handler(error) -> dict:
    return redirect(f'/login?next={request.path}')


# ------------------------ ERROR CODES ------------------------ #
@error_handling_bp.app_errorhandler(404)
async def not_found(error) -> str:
    return await render_template("404.html", data=await default_page_context_data())
