FROM python:3.9

RUN apt-get update && apt-get install -y vim zsh

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install poetry

COPY ./pyproject.toml /usr/src/app/
COPY ./poetry.lock /usr/src/app/
COPY ./README.rst /usr/src/app/
COPY ./tests /usr/src/app/
COPY ./planetmint_driver /usr/src/app/planetmint_driver

RUN adduser --system --group --home /nonroot nonroot 
USER nonroot

RUN poetry install --with dev