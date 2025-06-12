#!/bin/sh
set -e

echo "Waiting for the database to start..."
until nc -z db 5432; do
  echo "Waiting for Postgres..."
  sleep 1
done

echo "Running collectstatic..."
cd rag_engine
python manage.py collectstatic --noinput

echo "Applying migrations..."
python manage.py migrate

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
