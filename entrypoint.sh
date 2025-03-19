#!/bin/bash

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 portfolio.wsgi:application &

# Start Nginx
nginx -g 'daemon off;'

# Keep the script running so the container doesn't exit
wait