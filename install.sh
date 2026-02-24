#!/usr/bin/env bash
set -e

OS="$(uname -s)"

echo "==> Detected OS: $OS"

if [ "$OS" = "Linux" ]; then
    echo "==> Installing system packages (apt)..."
    sudo apt install -y python3-pyqt6 python3-libtorrent python3-lxml python3-pip

    echo "==> Installing Python packages..."
    pip3 install --user --break-system-packages requests beautifulsoup4

elif [ "$OS" = "Darwin" ]; then
    if ! command -v brew &>/dev/null; then
        echo "ERROR: Homebrew not found. Install it from https://brew.sh first."
        exit 1
    fi

    echo "==> Installing system packages (brew)..."
    brew install libtorrent-rasterbar

    echo "==> Installing Python packages..."
    pip3 install PyQt6 requests beautifulsoup4 lxml libtorrent

else
    echo "ERROR: Unsupported OS: $OS"
    exit 1
fi

echo ""
echo "✓ Done. Run with: python3 main.py"
