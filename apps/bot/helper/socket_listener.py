import asyncio
import json
import logging
import socket

import discord

from notilib import config


logger = logging.getLogger(__name__)

_socket_is_active = False


async def _dispatch_event(
    client: discord.Client,
    event_name: str,
    args: list,
    kwargs: dict
) -> None:
    client.dispatch(event_name, *args, **kwargs)


def start_socket_listener(client: discord.Client):
    # make sure function only gets run once
    global _socket_is_active
    if _socket_is_active:
        return
    _socket_is_active = True

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('0.0.0.0', config('apps.bot.socket_port')))
        server.listen()

        while True:
            conn = server.accept()[0]

            # decode data sent through socket and parse into dict
            try:
                data = conn.recv(1024).decode()
                json_data: dict = json.loads(data)
            except json.JSONDecodeError:
                logger.error(f'Failed to decode incoming json data from socket: {data}')
                continue

            # execute certain action based on received data
            match json_data.get('action'):
                case 'dispatch_event':
                    asyncio.run_coroutine_threadsafe(
                        coro=_dispatch_event(
                            client=client,
                            event_name=json_data.get('event_name'),
                            args=json_data.get('args', []),
                            kwargs=json_data.get('kwargs', {})
                        ),
                        loop=client.loop
                    )
