#!/usr/bin/env bash
set -e

OS="$(uname -s)"
INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"

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

# Create a launcher script so you can just run 'riffload' anywhere
echo "==> Installing riffload command..."
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/riffload" << EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/riffload"

# Make sure ~/.local/bin is in PATH (add to shell profile if missing)
for PROFILE in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$PROFILE" ] && ! grep -q '.local/bin' "$PROFILE"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
        echo "==> Added ~/.local/bin to PATH in $PROFILE"
    fi
done

# Update the desktop shortcut to use the launcher
if [ "$OS" = "Linux" ]; then
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    cat > "$DESKTOP_DIR/riffload.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Riffload
Comment=Music torrent browser
Exec=$BIN_DIR/riffload
Icon=$INSTALL_DIR/assets/icon_256.png
Terminal=false
Categories=Network;Audio;
EOF
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo ""
echo "✓ Done! Run it with:"
echo "   riffload"
echo ""
echo "  (If 'riffload' isn't found yet, open a new terminal or run: source ~/.bashrc)"
