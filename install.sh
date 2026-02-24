#!/usr/bin/env bash
set -e

OS="$(uname -s)"
INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"

# Detect Linux distro
DISTRO=""
if [ "$OS" = "Linux" ] && [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO="${ID_LIKE:-$ID}"
fi

echo "==> Detected: $OS ${DISTRO:+($DISTRO)}"

if [ "$OS" = "Linux" ]; then
    case "$DISTRO" in
        *arch*|*manjaro*|*endeavouros*)
            echo "==> Installing packages (pacman)..."
            sudo pacman -S --noconfirm --needed \
                python-pyqt6 \
                python-lxml \
                python-requests \
                python-beautifulsoup4 \
                python-pip

            # python-libtorrent is in the AUR; try pacman first then pip
            sudo pacman -S --noconfirm --needed python-libtorrent 2>/dev/null \
                || pip install --user libtorrent
            ;;

        *ubuntu*|*debian*|*pop*|*mint*|*neon*)
            echo "==> Installing packages (apt)..."
            sudo apt install -y \
                python3-pyqt6 \
                python3-libtorrent \
                python3-lxml \
                python3-pip

            echo "==> Installing Python packages..."
            pip3 install --user --break-system-packages requests beautifulsoup4
            ;;

        *fedora*|*rhel*|*centos*)
            echo "==> Installing packages (dnf)..."
            sudo dnf install -y \
                python3-qt6 \
                python3-libtorrent \
                python3-lxml \
                python3-pip

            pip3 install --user requests beautifulsoup4
            ;;

        *)
            echo "==> Unknown distro, trying pip for everything..."
            pip3 install --user PyQt6 requests beautifulsoup4 lxml libtorrent
            ;;
    esac

elif [ "$OS" = "Darwin" ]; then
    if ! command -v brew &>/dev/null; then
        echo "ERROR: Homebrew not found. Install it from https://brew.sh first."
        exit 1
    fi

    echo "==> Installing packages (brew + pip)..."
    brew install libtorrent-rasterbar
    pip3 install PyQt6 requests beautifulsoup4 lxml libtorrent

else
    echo "ERROR: Unsupported OS: $OS"
    exit 1
fi

# Create a launcher so you can just run 'riffload' anywhere
echo "==> Installing riffload command..."
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/riffload" << EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/riffload"

# Make sure ~/.local/bin is in PATH
for PROFILE in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.config/fish/config.fish"; do
    if [ -f "$PROFILE" ] && ! grep -q '.local/bin' "$PROFILE"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
        echo "==> Added ~/.local/bin to PATH in $PROFILE"
    fi
done

# Desktop shortcut (Linux only)
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
