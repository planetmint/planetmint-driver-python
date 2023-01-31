FROM python:3.9

RUN apt-get update && apt-get install -y vim zsh

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install poetry

COPY . /usr/src/app/

RUN poetry install --with dev