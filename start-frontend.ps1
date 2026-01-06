# PowerShell script to start the React frontend
# Usage: .\start-frontend.ps1

Write-Host "Starting React Frontend..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "npm found: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed" -ForegroundColor Red
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
VITE_API_BASE_URL=http://localhost:3001
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✅ Created .env file with VITE_API_BASE_URL=http://localhost:3001" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "Frontend Starting..." -ForegroundColor Green
Write-Host "Frontend will run on: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Make sure backend is running on: http://localhost:3001" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host ""

# Start the dev server
npm run dev

