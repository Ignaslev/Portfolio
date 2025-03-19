#!/bin/bash

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 main.wsgi:application &

# Wait for Gunicorn to be ready before starting Nginx
sleep 5

# Start Nginx
nginx -g 'daemon off;'

# Keep the script running so the container doesn't exit
wait