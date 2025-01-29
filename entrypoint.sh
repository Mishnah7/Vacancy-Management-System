#!/bin/sh

# Print environment information
echo "Environment Information:"
echo "RAILWAY_PRIVATE_DOMAIN: $RAILWAY_PRIVATE_DOMAIN"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "DATABASE_URL exists: $(if [ ! -z "$DATABASE_URL" ]; then echo "yes"; else echo "no"; fi)"

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
max_retries=30
counter=0

while ! nc -z $RAILWAY_PRIVATE_DOMAIN 5432; do
    counter=$((counter + 1))
    if [ $counter -ge $max_retries ]; then
        echo "Error: PostgreSQL did not become available in time"
        echo "RAILWAY_PRIVATE_DOMAIN: $RAILWAY_PRIVATE_DOMAIN"
        exit 1
    fi
    echo "Attempt $counter of $max_retries: PostgreSQL is not available yet..."
    sleep 2
done
echo "PostgreSQL is now available!"

# Create directories if they don't exist
echo "Creating necessary directories..."
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
    --log-level debug \
    --capture-output
