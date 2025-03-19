ARG PYTHON_VERSION=3.13-slim-bullseye
FROM python:${PYTHON_VERSION}

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY db.sqlite3 .
# Copy the project code
COPY . /app

# Define build argument
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

ARG DJANGO_DEBUG
ENV DJANGO_DEBUG=$DJANGO_DEBUG

# Explicitly create the database file if it doesn't exist
RUN python -c "from pathlib import Path; Path('db.sqlite3').touch()"

# Run migrations
RUN python manage.py migrate --noinput

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Set up entrypoint to run Gunicorn and Nginx
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

CMD ["entrypoint.sh"]