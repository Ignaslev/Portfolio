#!/bin/bash

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 main.wsgi:application &

# Start Nginx
nginx -g 'daemon off;'