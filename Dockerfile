FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=jobs.settings.production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles

# Copy project files
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Command to run the application
CMD ["/bin/sh", "entrypoint.sh"]
