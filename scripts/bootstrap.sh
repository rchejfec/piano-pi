#!/bin/bash
# ===========================================================================
# Piano Pi Brain — Bootstrap Script
#
# Run this on the Raspberry Pi to install everything:
#   chmod +x bootstrap.sh && sudo bash bootstrap.sh
#
# Pi 3 | OS Lite Legacy 64-bit | User: pi
# ===========================================================================

set -e

echo "============================================"
echo "  Piano Pi Brain — Bootstrap"
echo "============================================"
echo ""

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
echo "[1/6] Updating apt and installing packages..."
apt-get update -qq
apt-get install -y \
    fluidsynth \
    fluid-soundfont-gm \
    alsa-utils \
    python3-gpiozero \
    python3-pip

echo "  ✅ Packages installed"

# ---------------------------------------------------------------------------
# 2. Force audio output to 3.5mm headphone jack
# ---------------------------------------------------------------------------
echo "[2/6] Configuring audio output to 3.5mm jack..."

# Set ALSA default to the headphone jack (bcm2835 analog)
# For Pi OS Legacy, amixer controls the output
amixer cset numid=3 1 2>/dev/null || true  # 1 = headphone jack

# Also ensure dtparam=audio=on in config.txt
if ! grep -q "^dtparam=audio=on" /boot/config.txt 2>/dev/null; then
    echo "dtparam=audio=on" >> /boot/config.txt
fi

echo "  ✅ Audio set to 3.5mm jack"

# ---------------------------------------------------------------------------
# 3. Audio group + realtime permissions
# ---------------------------------------------------------------------------
echo "[3/6] Setting up audio permissions..."

# Add pi to audio group (likely already done, but just in case)
usermod -aG audio pi

# Set realtime scheduling limits for audio group
LIMITS_FILE="/etc/security/limits.conf"
if ! grep -q "@audio.*rtprio" "$LIMITS_FILE"; then
    echo "# Piano Pi — realtime audio scheduling" >> "$LIMITS_FILE"
    echo "@audio - rtprio 90" >> "$LIMITS_FILE"
    echo "@audio - memlock unlimited" >> "$LIMITS_FILE"
fi

echo "  ✅ Audio permissions configured"

# ---------------------------------------------------------------------------
# 4. Allow passwordless shutdown for pi user (for the off button)
# ---------------------------------------------------------------------------
echo "[4/6] Enabling passwordless shutdown..."

SUDOERS_FILE="/etc/sudoers.d/piano-pi-shutdown"
echo "pi ALL=(ALL) NOPASSWD: /sbin/shutdown" > "$SUDOERS_FILE"
chmod 440 "$SUDOERS_FILE"

echo "  ✅ Passwordless shutdown enabled"

# ---------------------------------------------------------------------------
# 5. Create project directory and set ownership
# ---------------------------------------------------------------------------
echo "[5/6] Setting up project directory..."

PROJECT_DIR="/home/pi/piano-pi-brain"
mkdir -p "$PROJECT_DIR"
chown -R pi:pi "$PROJECT_DIR"

echo "  ✅ Project directory ready at $PROJECT_DIR"

# ---------------------------------------------------------------------------
# 6. Test FluidSynth + SoundFont
# ---------------------------------------------------------------------------
echo "[6/6] Verifying FluidSynth installation..."

SOUNDFONT="/usr/share/sounds/sf2/FluidR3_GM.sf2"
if [ -f "$SOUNDFONT" ]; then
    echo "  ✅ SoundFont found: $SOUNDFONT"
else
    echo "  ❌ SoundFont NOT found at $SOUNDFONT"
    echo "     Try: apt-get install fluid-soundfont-gm"
    exit 1
fi

# Quick version check
FLUIDSYNTH_VERSION=$(fluidsynth --version 2>&1 | head -1)
echo "  ✅ $FLUIDSYNTH_VERSION"

echo ""
echo "============================================"
echo "  ✅ Bootstrap complete!"
echo ""
echo "  Next steps:"
echo "    1. Copy the Python files to $PROJECT_DIR"
echo "    2. Run: python3 $PROJECT_DIR/piano_pi.py"
echo "    3. Plug in your MIDI controller and play!"
echo "============================================"
