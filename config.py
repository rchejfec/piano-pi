"""
Piano Pi Brain — Configuration

Central config for GPIO pins, FluidSynth settings, and instrument list.
Edit this file to match your wiring and preferences.
"""

# ---------------------------------------------------------------------------
# GPIO Pin Assignments (BCM numbering)
# Wire each button between the GPIO pin and GND (gpiozero uses internal pull-ups)
# Wire each LED with a resistor (220Ω–330Ω) between the GPIO pin and the LED anode
# ---------------------------------------------------------------------------

BUTTON_RESTART = 17     # Short press = restart synth, Long press = shutdown
BUTTON_NEXT_INST = 27   # Next instrument
BUTTON_PREV_INST = 22   # Previous instrument

LED_RED = 24            # Single status LED (solid=ready, blink=shutting down)

# ---------------------------------------------------------------------------
# Button Timing
# ---------------------------------------------------------------------------

LONG_PRESS_SECONDS = 3.0     # Hold this long to trigger shutdown
DEBOUNCE_SECONDS = 0.05      # 50ms debounce (gpiozero default is fine)

# ---------------------------------------------------------------------------
# FluidSynth Settings (tuned for Raspberry Pi 3)
# ---------------------------------------------------------------------------

SOUNDFONT_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

FLUIDSYNTH_CMD = [
    "fluidsynth",
    "-a", "alsa",           # ALSA audio driver
    "-m", "alsa_seq",       # ALSA sequencer for MIDI
    "-r", "44100",          # Sample rate
    "-c", "3",              # Audio buffers (low = less latency)
    "-z", "128",            # Buffer size in samples
    "-g", "1.0",            # Gain (volume 0.0–10.0)
    "-o", "synth.polyphony=64",     # Max simultaneous notes
    "-o", "synth.cpu-cores=4",      # Use all Pi 3 cores
    "-C0",                  # Chorus off (save CPU)
    "-R0",                  # Reverb off (save CPU)
    # No -i or -s: runs in interactive mode, stays alive via stdin
]

# ---------------------------------------------------------------------------
# Instruments (General MIDI program numbers)
# Cycle through these with next/prev buttons
# ---------------------------------------------------------------------------

INSTRUMENTS = [
    {"name": "Acoustic Grand Piano",   "program": 0},
    {"name": "Bright Acoustic Piano",  "program": 1},
    {"name": "Electric Grand Piano",   "program": 2},
    {"name": "Honky-tonk Piano",       "program": 3},
    {"name": "Rhodes Piano",           "program": 4},
    {"name": "Chorused Piano",         "program": 5},
    {"name": "Harpsichord",            "program": 6},
    {"name": "Clavinet",               "program": 7},
    {"name": "Church Organ",           "program": 19},
    {"name": "Acoustic Guitar Nylon",  "program": 24},
    {"name": "Strings Ensemble",       "program": 48},
    {"name": "Synth Pad (warm)",       "program": 89},
]

DEFAULT_INSTRUMENT_INDEX = 0

# ---------------------------------------------------------------------------
# MIDI Settings
# ---------------------------------------------------------------------------

MIDI_CHANNEL = 4              # Keystation 49 MK3 sends on channel 4
MIDI_POLL_INTERVAL = 2.0      # Seconds between checking for new MIDI devices
