#!/bin/bash

until nc -z -w 50 datahubhel_db 5432
do
    echo "Connecting to database..."
    sleep 2
done

echo "Finished loading database"

echo "Apply database migrations"
./manage.py migrate --noinput

echo "Running server"
./manage.py runserver 0.0.0.0:8000
