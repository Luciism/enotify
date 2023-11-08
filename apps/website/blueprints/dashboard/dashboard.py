import logging

from quart import (
    Blueprint,
    render_template
)

from notilib.email_clients import gmail


logger = logging.getLogger(__name__)
logger.info('Blueprint registered.')


dashboard_bp = Blueprint(
    name='dashboard',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/dashboard/'
)


@dashboard_bp.route('/dashboard')
async def dashboard_route():
    data = {
        'user': {
            'avatar_url': 'https://cdn.discordapp.com/avatars/774848780234653726/f7cc9f66438939ae3be14490e205e7d9.webp',
            'email_accounts':  [
                {
                    'service_provider': 'gmail',
                    'email_address': 'example@gmail.com',
                    'email_address_redacted': '*******@gmail.com',
                    'sender_whitelist': {
                        'enabled': False,
                        'whitelisted_senders': [
                            'example@gmail.com',
                            'example@gmail.com',
                            'example@gmail.com',
                        ]
                    }
                },
                {
                    'service_provider': 'gmail',
                    'email_address': 'foo@gmail.com',
                    'email_address_redacted': '***@gmail.com',
                    'sender_whitelist': {
                        'enabled': True,
                        'whitelisted_senders': [
                            'example@gmail.com',
                            'example@gmail.com',
                            'example@gmail.com',
                        ]
                    }
                }
            ]
        },
        'gmail': {
            'auth_url': gmail.auth_url
        }
    }

    return await render_template('dashboard.html', data=data)
