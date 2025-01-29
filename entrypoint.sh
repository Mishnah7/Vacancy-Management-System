#!/bin/sh

echo "Starting application setup..."

# Print environment information
echo "\nEnvironment Information:"
echo "RAILWAY_PRIVATE_DOMAIN: $RAILWAY_PRIVATE_DOMAIN"
echo "DATABASE_URL exists: $(if [ ! -z "$DATABASE_URL" ]; then echo "yes"; else echo "no"; fi)"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "PORT: $PORT"

# Determine database host
DB_HOST=${RAILWAY_PRIVATE_DOMAIN:-localhost}
DB_PORT=${PGPORT:-5432}

echo "\nDatabase Connection Info:"
echo "Database Host: $DB_HOST"
echo "Database Port: $DB_PORT"

# Wait for database to be ready
echo "\nWaiting for PostgreSQL..."
max_retries=30
counter=0

while ! nc -z $DB_HOST $DB_PORT; do
    counter=$((counter + 1))
    if [ $counter -ge $max_retries ]; then
        echo "Error: PostgreSQL did not become available in time"
        echo "Last attempt details:"
        echo "Host: $DB_HOST"
        echo "Port: $DB_PORT"
        exit 1
    fi
    echo "Attempt $counter of $max_retries: PostgreSQL is not available yet..."
    sleep 2
done
echo "PostgreSQL is now available!"

# Create directories if they don't exist
echo "\nSetting up directories..."
mkdir -p /app/staticfiles
mkdir -p /app/mediafiles
echo "Directories created successfully"

# Collect static files
echo "\nCollecting static files..."
python manage.py collectstatic --noinput --clear
echo "Static files collected successfully"

# Run database migrations
echo "\nRunning database migrations..."
python manage.py migrate --noinput
echo "Migrations completed successfully"

# Start Gunicorn
echo "\nStarting Gunicorn..."
exec gunicorn jobs.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --reload
