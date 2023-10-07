import asyncio
import socket

import discord


def start_gmail_listener(client: discord.Client, queue: asyncio.Queue):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 15268))
    server.listen()

    while True:
        conn, _ = server.accept()
        data = conn.recv(1024).decode()

        if data:
            args = data.split(',')
            print('shit recieved: ' + str(args))
            asyncio.run_coroutine_threadsafe(
                coro=queue.put(('gmail_email_recieve', args)),
                loop=client.loop
            )
