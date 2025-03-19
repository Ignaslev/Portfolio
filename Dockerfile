FROM python:3.13-slim-bullseye

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# ENV DJANGO_SETTINGS_MODULE portfolio.main.settings

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app/

# Define build arguments
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

ARG DJANGO_DEBUG
ENV DJANGO_DEBUG=$DJANGO_DEBUG

# # Copy only the settings file first
# COPY main/settings.py portfolio/main/
#
# # Copy manage.py and the apps that need migrations
# COPY manage.py /app/
# COPY portfolio/__init__.py /app/portfolio/
# COPY burger_shop/ /app/burger_shop/

# Explicitly create the database file if it doesn't exist
RUN python -c "from pathlib import Path; Path('db.sqlite3').touch()"

# Run migrations
# RUN python manage.py migrate --database=burger_shop --noinput
# RUN python manage.py migrate --noinput
RUN DJANGO_SETTINGS_MODULE=portfolio.main.settings python manage.py migrate --database=burger_shop --noinput
RUN DJANGO_SETTINGS_MODULE=portfolio.main.settings python manage.py migrate --noinput

# Copy the rest of the project code
# COPY portfolio/ /app/portfolio/
# COPY . /app/  # This should copy everything else

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Set up entrypoint to run Gunicorn and Nginx
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

CMD ["entrypoint.sh"]