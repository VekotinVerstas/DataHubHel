FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /log
RUN mkdir /entrypoint

WORKDIR /backend

COPY ./backend .
COPY ./log /log
COPY ./django-entrypoint.sh /entrypoint/


RUN apt-get update && apt-get install -y \
    git \
    gdal-bin \
    python-gdal \
    python3-gdal \
    netcat

RUN pip install prequ

RUN prequ sync ./requirements*.txt

RUN chmod +x /entrypoint/django-entrypoint.sh
