FROM python:3.12-slim-bullseye AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    openssl \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    libxml2

FROM base AS dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT [ "/bin/bash", "-c", "python main.py"]
