import json
import socket

from notilib import config


json_data = json.dumps({'action': 'healthcheck'})

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(('bot', config('apps.bot.socket_port')))
        client.send(json_data.encode())
except ConnectionError:
    exit(1)
