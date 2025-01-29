#!/bin/sh

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z $PGHOST $PGPORT; do
    sleep 1
    echo "Still waiting for PostgreSQL..."
done
echo "PostgreSQL started successfully"

# Create directories if they don't exist
mkdir -p /app/staticfiles
mkdir -p /app/mediafiles

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn jobs.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
