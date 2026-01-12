#!/bin/bash

# Script to start the backend Flask server with Gunicorn
# Make sure you're in the backend directory or update the paths accordingly

cd "$(dirname "$0")/backend" || exit 1

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi

source venv/bin/activate

# Start Gunicorn
# -w 4: 4 worker processes
# -b 127.0.0.1:8080: Bind to localhost port 8080 (nginx will proxy to this)
# --timeout 300: 5 minute timeout for long-running scraping operations
# --access-logfile -: Log access to stdout
# --error-logfile -: Log errors to stdout
# app:app: Flask app instance

gunicorn -w 4 -b 127.0.0.1:8080 --timeout 300 --access-logfile - --error-logfile - app:app

