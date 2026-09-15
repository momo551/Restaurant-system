FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files at BUILD time with a dummy SECRET_KEY (safe for build only)
RUN SECRET_KEY=build-only-dummy-key python manage.py collectstatic --noinput || true

CMD ["sh", "-c", "until python manage.py migrate --noinput; do echo 'Database not ready, retrying in 5 seconds...'; sleep 5; done; echo 'Database ready - starting Daphne'; exec daphne -b 0.0.0.0 -p $PORT core.asgi:application"]