#!/usr/bin/env bash
set -e

OS="$(uname -s)"
ARCH="$(uname -m)"
VERSION=$(grep 'version' pyproject.toml | head -1 | grep -o '"[^"]*"' | tr -d '"')

echo "==> Building Riffload v$VERSION for $OS/$ARCH"

# Ensure PyInstaller is available
python3 -m PyInstaller --version &>/dev/null || pip3 install pyinstaller

if [ "$OS" = "Linux" ]; then
    echo "==> Building Linux binary..."
    python3 -m PyInstaller riffload.spec --noconfirm --clean

    BINARY="dist/riffload/riffload"
    OUTPUT="dist/riffload-${VERSION}-linux-${ARCH}.tar.gz"

    tar -czf "$OUTPUT" -C dist riffload/
    echo ""
    echo "✓ Built: $OUTPUT"
    echo "  Run with: tar -xzf $OUTPUT && ./riffload/riffload"

elif [ "$OS" = "Darwin" ]; then
    echo "==> Building macOS app bundle..."
    python3 -m PyInstaller riffload.spec --noconfirm --clean

    APP="dist/Riffload.app"
    DMG="dist/Riffload-${VERSION}-mac-${ARCH}.dmg"

    if command -v create-dmg &>/dev/null; then
        echo "==> Creating DMG..."
        create-dmg \
            --volname "Riffload ${VERSION}" \
            --window-pos 200 120 \
            --window-size 600 300 \
            --icon-size 100 \
            --icon "Riffload.app" 150 150 \
            --hide-extension "Riffload.app" \
            --app-drop-link 450 150 \
            "$DMG" \
            "$APP"
        echo ""
        echo "✓ Built: $DMG"
    else
        echo "  (install create-dmg for a DMG: brew install create-dmg)"
        echo ""
        echo "✓ Built: $APP"
        echo "  Drag Riffload.app to /Applications to install"
    fi

else
    echo "ERROR: Unsupported OS: $OS"
    exit 1
fi
