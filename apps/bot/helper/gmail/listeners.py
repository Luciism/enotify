import asyncio
import socket

import discord


recieved_listener_running = False


def start_gmail_recieved_listener(client: discord.Client, queue: asyncio.Queue):
    # make sure function only gets run once
    global recieved_listener_running
    if recieved_listener_running:
        return
    recieved_listener_running = True

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 15268))
    server.listen()

    while True:
        conn, _ = server.accept()
        data = conn.recv(1024).decode()

        if data:
            args = data.split(',')

            # put event information in queue using the bot's event loop
            asyncio.run_coroutine_threadsafe(
                coro=queue.put(('gmail_email_recieve', args)),
                loop=client.loop
            )
