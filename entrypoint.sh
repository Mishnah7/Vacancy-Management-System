#!/bin/sh

set -e  # Exit on error

echo "[$(date)] Starting application setup..."

# Function to check if PostgreSQL is ready
check_db() {
    nc -z -w2 "$1" "$2"
    return $?
}

# Function to wait for PostgreSQL
wait_for_db() {
    echo "[$(date)] Waiting for PostgreSQL..."
    local retries=30
    local host="${RAILWAY_PRIVATE_DOMAIN:-localhost}"
    local port="${PGPORT:-5432}"

    while [ "$retries" -gt 0 ]; do
        if check_db "$host" "$port"; then
            echo "[$(date)] PostgreSQL is available!"
            return 0
        fi
        retries=$((retries - 1))
        echo "[$(date)] Waiting for PostgreSQL... ($retries attempts left)"
        sleep 2
    done

    echo "[$(date)] Failed to connect to PostgreSQL after multiple attempts!"
    return 1
}

# Setup directories
echo "[$(date)] Setting up directories..."
mkdir -p /app/staticfiles /app/mediafiles

# Wait for database
wait_for_db || exit 1

# Django setup
echo "[$(date)] Running Django setup..."

echo "[$(date)] Collecting static files..."
python manage.py collectstatic --noinput --clear || {
    echo "[$(date)] Failed to collect static files!"
    exit 1
}

echo "[$(date)] Running database migrations..."
python manage.py migrate --noinput || {
    echo "[$(date)] Failed to run migrations!"
    exit 1
}

# Start Gunicorn
echo "[$(date)] Starting Gunicorn..."
exec gunicorn jobs.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output
