import asyncio
import os
import json
import socket
from enum import Enum
from typing import Callable
from collections.abc import Awaitable

import psycopg
from aiohttp import ClientSession, ClientError, ClientTimeout
from fastapi import FastAPI, Response, Request, WebSocket

from notilib import config

app = FastAPI()


API_KEY = os.getenv("health_api_key")
if API_KEY is None:
    raise RuntimeError("health_api_key is not set")


@app.get("/ready")
def is_ready():
    return Response(status_code=200)

class StatusEnum(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


async def get_postgres_status() -> StatusEnum:
    try:
        async with await psycopg.AsyncConnection.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            dbname=os.environ["POSTGRES_DB"],
            connect_timeout=3,
        ) as conn:
            cur = await conn.execute("SELECT 1")

            if await cur.fetchone() == (1,):
                return StatusEnum.HEALTHY
    except (psycopg.Error, TimeoutError):
        pass

    return StatusEnum.UNHEALTHY

def get_bot_status() -> StatusEnum:
    json_data = json.dumps({'action': 'healthcheck'})

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('bot', config('apps.bot.socket_port')))
            _ = client.send(json_data.encode())
            return StatusEnum.HEALTHY
    except (ConnectionError, OSError, TimeoutError):
        return StatusEnum.UNHEALTHY

async def get_website_status() -> StatusEnum:
    async with ClientSession() as session:
        try:
            res = await session.get("http://website:8000/", timeout=ClientTimeout(total=2))
            if res.status == 200:
                return StatusEnum.HEALTHY
        except (ClientError, OSError, TimeoutError) as exc:
            print(exc)

        return StatusEnum.UNHEALTHY

@app.middleware("http")
async def authenticate_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    api_key = request.headers.get("X-Api-Key")
    if api_key != API_KEY:
        return Response(status_code=401)

    response = await call_next(request)
    return response

@app.get("/health")
async def get_health() -> dict[str, dict[str, StatusEnum]]:
    return {"services": {
        "bot": get_bot_status(),
        "website": await get_website_status(),
        "database": await get_postgres_status(),
    }}


@app.websocket("/health")
async def send_health_periodically(websocket: WebSocket):
    api_key = websocket.headers.get("X-Api-Key")
    if api_key != API_KEY:
        await websocket.close(1008, "Unauthorized")
        return

    interval = 5
    try:
        interval = float(websocket.query_params.get("interval", interval))
    except (ValueError, TypeError):
        pass

    # Restrict to between 0.5
    interval = min(max(interval, 0.5), 60*60)

    await websocket.accept()

    while True:
        health = await get_health()
        await websocket.send_json(health)
        await asyncio.sleep(interval)
