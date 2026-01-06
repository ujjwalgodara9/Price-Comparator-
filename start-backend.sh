#!/bin/bash
# Bash script to start the Flask backend server
# Usage: ./start-backend.sh

echo "Starting Flask Backend Server..."
echo ""

# Change to backend directory
cd backend-example || exit 1

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi

echo "Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "============================================================"
echo "Backend Server Starting..."
echo "Server will run on: http://localhost:3001"
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the server
python3 server.py

