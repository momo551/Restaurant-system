FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files at BUILD time with a dummy SECRET_KEY (safe for build only)
RUN SECRET_KEY=build-only-dummy-key python manage.py collectstatic --noinput || true


# Run migrate, reset IP lockouts, create default users, then start server
# Using || true ensures the server starts even if setup commands fail temporarily
CMD ["sh", "-c", "\
echo STARTING && \
python manage.py migrate --noinput || true && \
python manage.py collectstatic --noinput || true && \
daphne -b 0.0.0.0 -p $PORT core.asgi:application \
"]