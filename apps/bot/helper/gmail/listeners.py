import asyncio
import socket

import discord

from notilib import config

recieved_listener_running = False


def start_gmail_recieved_listener(client: discord.Client, queue: asyncio.Queue):
    # make sure function only gets run once
    global recieved_listener_running
    if recieved_listener_running:
        return
    recieved_listener_running = True

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('127.0.0.1', config('global.gmail_recieve_socket_port')))
        server.listen()

        while True:
            conn, _ = server.accept()
            email_address = conn.recv(1024).decode()

            if email_address:
                # put event information in queue using the bot's event loop
                asyncio.run_coroutine_threadsafe(
                    coro=queue.put(('gmail_email_recieve', email_address)),
                    loop=client.loop
                )
