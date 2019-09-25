#!/bin/bash

check_db_connection_script="
from django.db import connection
try:
    connection.connect()
except Exception as error:
    raise SystemExit(error)
"
until ./manage.py shell -c "$check_db_connection_script"; do
    echo "Waiting for database to come up..."
    sleep 1
done
echo "Database seems to be ready."

echo "Apply database migrations"
./manage.py migrate --noinput

echo "Running server"
./manage.py runserver 0.0.0.0:8000
