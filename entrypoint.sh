#!/bin/bash

# Apply migrations
python manage.py migrate --noinput

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 your_project.wsgi