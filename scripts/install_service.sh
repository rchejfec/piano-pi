#!/bin/bash
# ===========================================================================
# Piano Pi Brain — Install Service
#
# Run AFTER bootstrap.sh and copying Python files to /home/pi/piano-pi-brain
#   sudo bash install_service.sh
# ===========================================================================

set -e

SERVICE_SRC="/home/pi/piano-pi-brain/services/piano-pi.service"
SERVICE_DST="/etc/systemd/system/piano-pi.service"

echo "Installing Piano Pi systemd service..."

cp "$SERVICE_SRC" "$SERVICE_DST"
systemctl daemon-reload
systemctl enable piano-pi
systemctl start piano-pi

echo "✅ Service installed and started!"
echo ""
echo "Commands:"
echo "  Status:   sudo systemctl status piano-pi"
echo "  Logs:     journalctl -u piano-pi -f"
echo "  Stop:     sudo systemctl stop piano-pi"
echo "  Restart:  sudo systemctl restart piano-pi"
