#!/bin/bash

# Fast E-commerce Product Compare - Setup Script for Linux
# This script sets up the Python 3.11 environment and installs dependencies

set -e  # Exit on any error

echo "=========================================="
echo "Fast E-commerce Product Compare Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This script is for Linux only${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python 3.11
echo -e "${YELLOW}Checking for Python 3.11...${NC}"
if command_exists python3.11; then
    PYTHON_CMD="python3.11"
    echo -e "${GREEN}✓ Python 3.11 found${NC}"
elif command_exists python3 && python3 --version | grep -q "3.11"; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✓ Python 3.11 found (as python3)${NC}"
else
    echo -e "${RED}✗ Python 3.11 not found${NC}"
    echo "Please install Python 3.11 first:"
    echo "  Ubuntu/Debian: sudo apt-get update && sudo apt-get install python3.11 python3.11-venv python3.11-dev"
    echo "  Fedora/RHEL: sudo dnf install python3.11 python3.11-devel"
    echo "  Or build from source: https://www.python.org/downloads/"
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check if version is 3.11.x
if [[ ! "$PYTHON_VERSION" =~ ^3\.11\. ]]; then
    echo -e "${RED}Error: Python 3.11.x is required, but found $PYTHON_VERSION${NC}"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Create virtual environment
echo ""
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Removing old one...${NC}"
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
echo ""
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install system dependencies (for Playwright)
echo ""
echo -e "${YELLOW}Checking for system dependencies...${NC}"
if command_exists apt-get; then
    echo "Detected apt-get (Ubuntu/Debian)"
    echo "If Playwright fails, install dependencies with:"
    echo "  sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2"
elif command_exists dnf; then
    echo "Detected dnf (Fedora/RHEL)"
    echo "If Playwright fails, install dependencies with:"
    echo "  sudo dnf install -y nss nspr atk at-spi2-atk cups-libs libdrm libXkbcommon libXcomposite libXdamage libXfixes libXrandr mesa-libgbm alsa-lib"
fi

# Install Python dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Install Playwright browsers
echo ""
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
playwright install chromium
echo -e "${GREEN}✓ Playwright browsers installed${NC}"

# Go back to root
cd ..

# Install Node.js v24.11.1 using nvm
echo ""
echo -e "${YELLOW}Setting up Node.js v24.11.1...${NC}"

# Check if nvm is installed
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo -e "${GREEN}✓ nvm found${NC}"
    source "$HOME/.nvm/nvm.sh"
elif [ -s "/usr/local/opt/nvm/nvm.sh" ]; then
    echo -e "${GREEN}✓ nvm found (system-wide)${NC}"
    source "/usr/local/opt/nvm/nvm.sh"
else
    echo -e "${YELLOW}Installing nvm (Node Version Manager)...${NC}"
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    echo -e "${GREEN}✓ nvm installed${NC}"
fi

# Source nvm to make it available in this script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check current Node.js version
if command_exists node; then
    CURRENT_NODE_VERSION=$(node --version)
    echo "Current Node.js version: $CURRENT_NODE_VERSION"
    
    # Check if it's already v24.11.1
    if [ "$CURRENT_NODE_VERSION" == "v24.11.1" ]; then
        echo -e "${GREEN}✓ Node.js v24.11.1 already installed${NC}"
    else
        echo -e "${YELLOW}Installing Node.js v24.11.1...${NC}"
        nvm install 24.11.1
        nvm use 24.11.1
        nvm alias default 24.11.1
        echo -e "${GREEN}✓ Node.js v24.11.1 installed and set as default${NC}"
    fi
else
    echo -e "${YELLOW}Installing Node.js v24.11.1...${NC}"
    nvm install 24.11.1
    nvm use 24.11.1
    nvm alias default 24.11.1
    echo -e "${GREEN}✓ Node.js v24.11.1 installed and set as default${NC}"
fi

# Verify Node.js installation
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ Node.js: $NODE_VERSION${NC}"
echo -e "${GREEN}✓ npm: $NPM_VERSION${NC}"

# Install frontend dependencies (optional)
echo ""
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}package.json not found, skipping frontend dependencies${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source backend/venv/bin/activate"
echo ""
echo "To run the backend server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Or with gunicorn (production):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  gunicorn --bind 0.0.0.0:8080 app:app"
echo ""
echo "To run the frontend (after activating nvm):"
echo "  source ~/.nvm/nvm.sh  # or add to your .bashrc/.zshrc"
echo "  npm run dev"
echo ""
echo "Note: Add nvm to your shell profile (~/.bashrc or ~/.zshrc) to use it permanently:"
echo "  export NVM_DIR=\"\$HOME/.nvm\""
echo "  [ -s \"\$NVM_DIR/nvm.sh\" ] && \. \"\$NVM_DIR/nvm.sh\""
echo ""

