#!/bin/bash
# Bash script to start the React frontend
# Usage: ./start-frontend.sh

echo "Starting React Frontend..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

echo "npm found: $(npm --version)"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "VITE_API_BASE_URL=http://localhost:3001" > .env
    echo "✅ Created .env file with VITE_API_BASE_URL=http://localhost:3001"
fi

echo ""
echo "============================================================"
echo "Frontend Starting..."
echo "Frontend will run on: http://localhost:5173"
echo "Make sure backend is running on: http://localhost:3001"
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the dev server
npm run dev

