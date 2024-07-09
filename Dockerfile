FROM python:3.12.4-slim-bullseye

RUN apt-get update
RUN apt-get install -y curl

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY . /app/
RUN pip install -e /app

WORKDIR /app
