FROM python:3.11.7-slim-bullseye

WORKDIR /app

RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --group=bot --frozen

COPY ./config.json .
COPY ./apps/bot bot
COPY ./notilib notilib

ENV PYTHONPATH /app
WORKDIR /app/bot
ENTRYPOINT ["/app/.venv/bin/python3", "main.py"]
