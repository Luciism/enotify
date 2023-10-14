import asyncio
import socket

import discord

from notilib import config

received_listener_running = False


def start_gmail_received_listener(client: discord.Client, queue: asyncio.Queue):
    # make sure function only gets run once
    global received_listener_running
    if received_listener_running:
        return
    received_listener_running = True

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('127.0.0.1', config('global.gmail_receive_socket_port')))
        server.listen()

        while True:
            conn, _ = server.accept()
            email_address = conn.recv(1024).decode()

            if email_address:
                # put event information in queue using the bot's event loop
                asyncio.run_coroutine_threadsafe(
                    coro=queue.put(('gmail_email_receive', email_address)),
                    loop=client.loop
                )
