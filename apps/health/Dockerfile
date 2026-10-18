FROM python:3.11.7-slim-bullseye AS base

FROM base AS deps

WORKDIR /app

RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --group=health --frozen


FROM deps AS builder

WORKDIR /app


COPY ./apps/health/ health/
COPY ./notilib notilib/
COPY ./config.json .


FROM builder AS runner

ENV PYTHONPATH /app
WORKDIR /app/health
ENTRYPOINT [ "/app/.venv/bin/fastapi", "run", "app.py", "--host=0.0.0.0", "--port=8000", "--workers=2"]
