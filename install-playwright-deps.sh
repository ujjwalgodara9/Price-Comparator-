#!/bin/bash

# Script to install Playwright system dependencies on Linux
# This fixes the "libatk-1.0.so.0: cannot open shared object file" error

echo "Installing Playwright system dependencies..."

# Detect package manager
if command -v apt-get >/dev/null 2>&1; then
    echo "Detected apt-get (Ubuntu/Debian)"
    sudo apt-get update -qq
    sudo apt-get install -y \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libxshmfence1 \
        libxcb1 \
        libx11-6 \
        libx11-xcb1 \
        libxcursor1 \
        libxi6 \
        libxtst6 \
        libpangocairo-1.0-0 \
        libcairo-gobject2 \
        libgtk-3-0 \
        libgdk-pixbuf2.0-0
    echo "✓ Dependencies installed"
elif command -v dnf >/dev/null 2>&1; then
    echo "Detected dnf (Fedora/RHEL)"
    sudo dnf install -y \
        nss \
        nspr \
        atk \
        at-spi2-atk \
        cups-libs \
        libdrm \
        libXkbcommon \
        libXcomposite \
        libXdamage \
        libXfixes \
        libXrandr \
        mesa-libgbm \
        alsa-lib \
        libxshmfence \
        libX11 \
        libX11-xcb \
        libxcb \
        libXcursor \
        libXi \
        libXtst \
        pango \
        cairo-gobject \
        gtk3 \
        gdk-pixbuf2
    echo "✓ Dependencies installed"
else
    echo "Error: Unknown package manager. Please install Playwright dependencies manually."
    echo "See: https://playwright.dev/python/docs/deps"
    exit 1
fi

echo ""
echo "Playwright system dependencies installed successfully!"
echo "You may need to restart your application for changes to take effect."

