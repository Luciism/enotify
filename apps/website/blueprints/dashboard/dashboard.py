import logging

from quart import (
    Blueprint,
    render_template,
    request,
    redirect
)

from notilib import (
    EmailNotificationFilters,
    get_all_email_addresses,
    remove_email_address
)
from helper import (
    discord_auth_client,
    response_msg,
    is_email_address_valid,
    page_user_context_data
)


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
            'valid': email_address['valid'],
            'email_address_redacted': redact_email_address(email_address['email_address']),
            'sender_whitelist': {
                'enabled': await filters.sender_whitelist_enabled,
                'whitelisted_senders': await filters.whitelisted_senders
            },
            'sender_blacklist': {
                'blacklisted_senders': await filters.blacklisted_senders
            }
        }
        email_accounts_data.append(email_account_data)

    return email_accounts_data


@dashboard_bp.route('/dashboard')
async def dashboard_route():
    user = await discord_auth_client.authenticate_user()

    data = {
        'user': {
            **page_user_context_data(user),
            'email_accounts': await _build_email_accounts_data(user.id)
        }
    }

    return await render_template('dashboard.html', data=data)


@dashboard_bp.route(
    '/dashboard/api/add-or-remove-filtered-sender', methods=['POST'])
async def add_or_remove_filtered_sender():
    user = await discord_auth_client.authenticate_user()

    # get and validate request data
    request_data: dict = await request.get_json()

    try:
        email_account_data: dict = request_data['email_account_data']
        email_address: str = email_account_data['email_address']
        webmail_service: str = email_account_data['webmail_service']

        sender_email_address: str = request_data['sender_email_address']
        sender_filter: str = request_data['filter']
        action: str = request_data['action']
    except KeyError:
        return response_msg('invalid_request_data')

    # make sure options are valid
    if sender_filter not in ('whitelist', 'blacklist') \
                    or action not in ('add', 'remove'):
        return response_msg('invalid_request_data')

    filters = EmailNotificationFilters(user.id, email_address, webmail_service)

    match sender_filter:
        case 'whitelist':
            match action:
                case 'add':
                    # make sure email address is a valid format before adding
                    if not is_email_address_valid(sender_email_address):
                        return response_msg('invalid_email_address_format')

                    await filters.add_whitelisted_sender(sender_email_address)
                case 'remove':
                    await filters.remove_whitelisted_sender(sender_email_address)

        case 'blacklist':
            match action:
                case 'add':
                    if not is_email_address_valid(sender_email_address):
                        return response_msg('invalid_email_address_format')

                    await filters.add_blacklisted_sender(sender_email_address)
                case 'remove':
                    await filters.remove_blacklisted_sender(sender_email_address)

    return response_msg('edit_filtered_sender_success')


@dashboard_bp.route(
    '/dashboard/api/edit-filtered-sender', methods=['POST'])
async def edit_filtered_sender():
    user = await discord_auth_client.authenticate_user()

    # get and validate request data
    request_data: dict = await request.get_json()

    try:
        email_account_data: dict = request_data['email_account_data']
        email_address: str = email_account_data['email_address']
        webmail_service: str = email_account_data['webmail_service']

        sender_email_address_old: str = request_data['sender_email_address_old']
        sender_email_address_new: str = request_data['sender_email_address_new']
        sender_filter: str = request_data['filter']
    except KeyError:
        return response_msg('invalid_request_data')

    # make sure options are valid
    if sender_filter not in ('whitelist', 'blacklist'):
        return response_msg('invalid_request_data')

    filters = EmailNotificationFilters(user.id, email_address, webmail_service)

    match sender_filter:
        case 'whitelist':
            await filters.remove_whitelisted_sender(sender_email_address_old)
            await filters.add_whitelisted_sender(sender_email_address_new)
        case 'blacklist':
            await filters.remove_blacklisted_sender(sender_email_address_old)
            await filters.add_blacklisted_sender(sender_email_address_new)

    return response_msg('edit_filtered_sender_success')


@dashboard_bp.route(
    '/dashboard/api/toggle-sender-whitelist', methods=['POST'])
async def toggle_whitelisted_sender():
    user = await discord_auth_client.authenticate_user()

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
    user = await discord_auth_client.authenticate_user()

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
