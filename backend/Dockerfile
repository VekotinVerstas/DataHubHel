FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    git \
    gdal-bin \
    python-gdal \
    python3-gdal \
    netcat

WORKDIR /app

RUN pip install prequ
COPY requirements*.txt ./
RUN prequ sync ./requirements*.txt

COPY . .

RUN mkdir /var/log/datahubhel
RUN mkdir /var/lib/datahubhel
ENV LOG_ROOT /var/log/datahubhel
ENV VAR_ROOT /var/lib/datahubhel

ENTRYPOINT [ "/app/django-entrypoint.sh" ]
