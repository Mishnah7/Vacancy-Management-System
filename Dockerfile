FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set up environment file
RUN cp .env.dev.sample .env || echo "DEBUG=False\nSECRET_KEY=your-secret-key-here\nALLOWED_HOSTS=.railway.app" > .env

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV PORT=8000
ENV APP_HOME=/app
ENV DJANGO_SETTINGS_MODULE=jobs.settings.production

# Run entrypoint script
CMD ["./entrypoint.sh"]
