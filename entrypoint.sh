#!/bin/sh

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z $PGHOST $PGPORT; do
    sleep 0.1
done
echo "PostgreSQL started"

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start Gunicorn
gunicorn jobs.wsgi:application --bind 0.0.0.0:$PORT
