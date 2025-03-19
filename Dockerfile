ARG PYTHON_VERSION=3.13-slim-bullseye
FROM python:${PYTHON_VERSION}

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY db.sqlite3 .
# Copy the project code
COPY . /app

# Define build arguments for AWS credentials and bucket name
ARG AWS_ACCESS_KEY_ID
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID

ARG AWS_SECRET_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

ARG AWS_STORAGE_BUCKET_NAME
ENV AWS_STORAGE_BUCKET_NAME=$AWS_STORAGE_BUCKET_NAME

ARG AWS_S3_REGION_NAME
ENV AWS_S3_REGION_NAME=$AWS_S3_REGION_NAME

# You can also do this for AWS_S3_SIGNATURE_VERSION if you have it
ARG AWS_S3_SIGNATURE_VERSION
ENV AWS_S3_SIGNATURE_VERSION=$AWS_S3_SIGNATURE_VERSION

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


# Set up entrypoint to run Gunicorn and Nginx
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000
EXPOSE 80



CMD ["entrypoint.sh"]