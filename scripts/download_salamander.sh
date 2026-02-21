#!/bin/bash
# Download Salamander Grand Piano SoundFont (Lite version, ~24MB)
# Run on the Pi: bash scripts/download_salamander.sh

set -e

DEST_DIR="/home/pi/piano-pi-brain/soundfonts"
DEST_FILE="$DEST_DIR/SalamanderGrandPiano.sf2"
URL="https://musical-artifacts.com/artifacts/1011/SalC5Light2.sf2"

# Remove oversized full version if it exists
if [ -f "$DEST_FILE" ] && [ $(stat -c%s "$DEST_FILE" 2>/dev/null || stat -f%z "$DEST_FILE") -gt 100000000 ]; then
    echo "Removing oversized full version..."
    rm "$DEST_FILE"
fi

if [ -f "$DEST_FILE" ]; then
    echo "✅ Salamander Grand Piano Lite already downloaded"
    exit 0
fi

echo "Downloading Salamander Grand Piano Lite SoundFont (~24MB)..."
mkdir -p "$DEST_DIR"

curl -L -o "$DEST_FILE" "$URL"

echo "✅ Salamander Grand Piano Lite installed at $DEST_FILE"
ls -lh "$DEST_FILE"
