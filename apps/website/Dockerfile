FROM python:3.11.7-slim-bullseye

WORKDIR /app

COPY ./apps/website/requirements.txt website/requirements.txt
RUN pip install -r website/requirements.txt

COPY ./notilib/requirements.txt notilib/requirements.txt
RUN pip install -r notilib/requirements.txt

COPY ./config.json .
COPY ./apps/website website
COPY ./notilib notilib

EXPOSE 8000

ENV PYTHONPATH /app
WORKDIR /app/website
ENTRYPOINT ["hypercorn", "app:app", "--bind=0.0.0.0:8000", "--workers=3"]
