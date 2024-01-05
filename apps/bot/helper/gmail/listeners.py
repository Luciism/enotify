import asyncio
import json
import socket
import logging

import discord

from notilib import config


logger = logging.getLogger(__name__)

received_listener_running = False


def start_gmail_received_listener(client: discord.Client, queue: asyncio.Queue):
    # make sure function only gets run once
    global received_listener_running
    if received_listener_running:
        return
    received_listener_running = True

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('0.0.0.0', config('apps.bot.socket_port')))
        server.listen()

        while True:
            conn, _ = server.accept()

            try:
                data = conn.recv(1024).decode()
                json_data: dict = json.loads(data)
            except json.JSONDecodeError:
                logger.error(f'Failed to decode incoming json data from socket: {data}')
                continue

            match json_data.get('action'):
                case 'dispatch_event':
                    asyncio.run_coroutine_threadsafe(
                        coro=queue.put(
                            item=(
                                json_data.get('event_name'),
                                json_data.get('args', []),
                                json_data.get('kwargs', {})
                            )
                        ),
                        loop=client.loop
                    )
