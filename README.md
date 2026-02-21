> Weekend project to turn a Raspberry Pi into a standalone practice piano. Built with Claude Opus 4.

# Piano Pi Brain 🎹

A standalone MIDI piano practice device on a Raspberry Pi 3. Plug in a USB MIDI controller, power on, and play — no computer needed.

## What It Does

- **Auto-starts on boot** — powered by systemd, no SSH required
- **Auto-detects MIDI controllers** — hotplug support, reconnects automatically
- **Instrument switching** — cycle through GM sounds with breadboard buttons
- **Web portal** — phone-friendly UI at `http://<pi-ip>:8080` for instrument selection, restart, and shutdown
- **LED status indicator** — single red LED: solid = ready, blink patterns for starting/error
- **Safe shutdown** — long-press button to safely power down before unplugging
- **Error recovery** — auto-restarts FluidSynth if it crashes

## Hardware

| Component | Details |
|-----------|---------|
| Pi | Raspberry Pi 3, OS Lite Legacy 64-bit |
| Audio | 3.5mm jack → speaker (or MonkMakes Amplified Speaker 2) |
| MIDI | M-Audio Keystation 49 MK3 / Arturia MiniLab 3 (any USB MIDI works) |
| Buttons | 3 push buttons on breadboard |
| LED | 1 red LED on GPIO 24 |

## Wiring

### Buttons (GPIO pin → button → GND)

| Button | GPIO (BCM) | Pi Pin | Function |
|--------|-----------|--------|----------|
| Restart / Shutdown | 17 | 11 | Short press = restart, hold 3s = shutdown |
| Next Instrument | 27 | 13 | Cycle to next sound |
| Prev Instrument | 22 | 15 | Cycle to previous sound |

### LED (GPIO pin → 220Ω resistor → LED anode → LED cathode → GND)

| LED | GPIO (BCM) | Pi Pin |
|-----|-----------|--------|
| Red (status) | 24 | 18 |

## Setup

```bash
# 1. Run bootstrap (installs FluidSynth, configures audio + permissions)
sudo bash scripts/bootstrap.sh

# 2. Test manually
cd /home/pi/piano-pi-brain && python3 piano_pi.py

# 3. Install auto-start service
sudo cp services/piano-pi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable piano-pi
sudo reboot
```

## LED Status (Red LED)

| Pattern | Meaning |
|---------|---------|
| Solid | Ready to play |
| Blink (0.3s) | Starting up — wait |
| Fast blink (0.1s) | Shutting down — safe to unplug when off |
| Uneven blink (0.8/0.2s) | Error — press restart button |

## Instruments

Cycle through with the Next/Prev buttons:

1. Acoustic Grand Piano
2. Bright Acoustic Piano
3. Electric Grand Piano
4. Honky-tonk Piano
5. Rhodes Piano
6. Chorused Piano
7. Harpsichord
8. Clavinet
9. Church Organ
10. Acoustic Guitar (Nylon)
11. Strings Ensemble
12. Synth Pad (Warm)

## Project Structure

```
piano_pi.py        Main orchestrator — ties everything together
config.py          GPIO pins, FluidSynth settings, instrument list
synth.py           FluidSynth subprocess manager
buttons.py         Button handler with long-press detection
leds.py            Single-LED status indicator
midi_monitor.py    MIDI auto-detect + hotplug
scripts/
  bootstrap.sh     First-run setup script
  install_service.sh  Installs systemd auto-start
services/
  piano-pi.service  systemd unit file
docs/
  WIRING_GUIDE.md   Beginner breadboard wiring guide
```

## Configuration

Edit `config.py` to change:
- GPIO pin assignments
- FluidSynth audio settings
- MIDI channel (default: 4 for Keystation 49 MK3)
- Instrument list

## Troubleshooting

```bash
# Service status
sudo systemctl status piano-pi

# Live logs
journalctl -u piano-pi -f

# List audio devices
aplay -l

# List MIDI devices
aconnect -l

# Monitor raw MIDI input
aseqdump -p <client_id>:0

# Test speaker
speaker-test -t wav -c 2
```
