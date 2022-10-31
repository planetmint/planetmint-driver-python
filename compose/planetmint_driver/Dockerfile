FROM python:3.9

RUN apt-get update && apt-get install -y vim zsh

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY . /usr/src/app/

RUN pip install --no-cache-dir -e .[dev]
RUN pip install sphinx-press-theme==0.8.0