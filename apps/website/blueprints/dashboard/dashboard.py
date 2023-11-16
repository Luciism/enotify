import logging

from quart import (
    Blueprint,
    render_template,
    request,
    session
)

from notilib import (
    EmailNotificationFilters,
    get_all_email_addresses,
    remove_email_address
)
from helper import fetch_discord_user, response_msg, is_email_address_valid


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')


dashboard_bp = Blueprint(
    name='dashboard',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/dashboard/'
)


def redact_email_address(email_address: str) -> str:
    start, end = email_address.rsplit('@', maxsplit=1)

    return f'{"*"*len(start)}@{end}'


async def _build_email_accounts_data(user_id: int) -> list[dict]:
    all_email_addresses = await get_all_email_addresses(user_id)
    email_accounts_data = []

    for email_address in all_email_addresses:
        filters = EmailNotificationFilters(
            user_id, email_address['email_address'], email_address['webmail_service'])


        email_account_data = {
            'webmail_service': email_address['webmail_service'],
            'email_address': email_address['email_address'],
            'email_address_redacted': redact_email_address(email_address['email_address']),
            'sender_whitelist': {
                'enabled': await filters.sender_whitelist_enabled,
                'whitelisted_senders': await filters.whitelisted_senders
            }
        }
        email_accounts_data.append(email_account_data)

    print(email_accounts_data)
    return email_accounts_data


@dashboard_bp.route('/dashboard')
async def dashboard_route():
    # validate user
    access_token = session.get('access_token')
    user = await fetch_discord_user(access_token)

    if user is None:
        return response_msg('invalid_discord_access_token')

    data = {
        'user': {
            'avatar_url': user.avatar_url,
            'email_accounts': await _build_email_accounts_data(user.id)
        }
    }

    return await render_template('dashboard.html', data=data)


@dashboard_bp.route(
    '/dashboard/api/remove-whitelisted-sender', methods=['POST'])
async def remove_whitelisted_sender():
    # validate user
    access_token = session.get('access_token')
    user = await fetch_discord_user(access_token, cache=True)

    if user is None:
        return response_msg('invalid_discord_access_token')

    # get and validate request data
    request_data: dict = await request.get_json()

    try:
        email_account_data: dict = request_data['email_account_data']
        email_address: str = email_account_data['email_address']
        webmail_service: str = email_account_data['webmail_service']

        sender_email_address: str = request_data['sender_email_address']
    except KeyError:
        return response_msg('invalid_request_data')

    filters = EmailNotificationFilters(user.id, email_address, webmail_service)
    await filters.remove_whitelisted_sender(sender_email_address)

    return response_msg('remove_whitelisted_sender_success')


@dashboard_bp.route(
    '/dashboard/api/add-whitelisted-sender', methods=['POST'])
async def add_whitelisted_sender():
    # validate user
    access_token = session.get('access_token')
    user = await fetch_discord_user(access_token, cache=True)

    if user is None:
        return response_msg('invalid_discord_access_token')

    # get and validate request data
    request_data: dict = await request.get_json()

    try:
        email_account_data: dict = request_data['email_account_data']
        email_address: str = email_account_data['email_address']
        webmail_service: str = email_account_data['webmail_service']

        sender_email_address: str = request_data['sender_email_address']
    except KeyError:
        return response_msg('invalid_request_data')

    if not is_email_address_valid(sender_email_address):
        return response_msg('invalid_email_address_format')

    filters = EmailNotificationFilters(user.id, email_address, webmail_service)
    await filters.add_whitelisted_sender(sender_email_address)

    return response_msg('add_whitelisted_sender_success')


@dashboard_bp.route(
    '/dashboard/api/toggle-sender-whitelist', methods=['POST'])
async def toggle_whitelisted_sender():
    # validate user
    access_token = session.get('access_token')
    user = await fetch_discord_user(access_token, cache=True)

    if user is None:
        return response_msg('invalid_discord_access_token')

    # get and validate request data
    request_data: dict = await request.get_json()

    try:
        email_account_data: dict = request_data['email_account_data']
        email_address: str = email_account_data['email_address']
        webmail_service: str = email_account_data['webmail_service']

        enabled: str = request_data['enabled']
    except KeyError:
        return response_msg('invalid_request_data')

    filters = EmailNotificationFilters(user.id, email_address, webmail_service)
    await filters.set_sender_whitelist_enabled(enabled)

    return response_msg('toggle_sender_whitelist_success')


@dashboard_bp.route(
    '/dashboard/api/remove-email-account', methods=['POST'])
async def remove_email_account():
    # validate user
    access_token = session.get('access_token')
    user = await fetch_discord_user(access_token, cache=True)

    if user is None:
        return response_msg('invalid_discord_access_token')

    # get and validate request data
    request_data: dict = await request.get_json()

    try:
        email_account_data: dict = request_data['email_account_data']
        email_address: str = email_account_data['email_address']
        webmail_service: str = email_account_data['webmail_service']
    except KeyError:
        return response_msg('invalid_request_data')

    await remove_email_address(user.id, email_address, webmail_service)
    return response_msg('remove_email_account_success')
