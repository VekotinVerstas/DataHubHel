FROM python:3.7-slim as appbase

ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN mkdir /var/log/datahubhel
RUN mkdir /var/lib/datahubhel
ENV LOG_ROOT /var/log/datahubhel
ENV VAR_ROOT /var/lib/datahubhel

COPY requirements.txt ./requirements.txt

RUN apt-get update \
    && \
    apt-get install --no-install-recommends -y \
      gdal-bin \
      python3-gdal \
      netcat \
      libpq-dev \
      build-essential \
    && \
    pip install --no-cache-dir -r requirements.txt \
    && \
    apt-get remove -y build-essential libpq-dev \
    && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && \
    rm -rf /var/lib/apt/lists/* \
    && \
    rm -rf /var/cache/apt/archives

COPY . .

ENTRYPOINT [ "/app/django-entrypoint.sh" ]

# Production docker environment
FROM appbase as production

RUN chown www-data /var/log/datahubhel
RUN chown www-data /var/lib/datahubhel

USER www-data

CMD ["production"]

# Development docker environment
FROM appbase as development

COPY requirements-*.txt ./

RUN pip install --no-cache-dir \
    -r requirements-stylecheck.txt \
    -r requirements-test.txt

CMD ["development"]
