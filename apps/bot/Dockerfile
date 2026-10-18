FROM python:3.11.7-slim-bullseye

WORKDIR /app

RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --group=bot --frozen

# COPY ./apps/bot/requirements.txt bot/requirements.txt
# RUN pip install -r bot/requirements.txt
#
# COPY ./notilib/requirements.txt notilib/requirements.txt
# RUN pip install -r notilib/requirements.txt

COPY ./config.json .
COPY ./apps/bot bot
COPY ./notilib notilib

ENV PYTHONPATH /app
WORKDIR /app/bot
ENTRYPOINT ["/app/.venv/bin/python3", "main.py"]
