"""
Piano Pi Brain — Configuration

Central config for GPIO pins, FluidSynth settings, and instrument list.
Edit this file to match your wiring and preferences.
"""

# ---------------------------------------------------------------------------
# GPIO Pin Assignments (BCM numbering)
# ---------------------------------------------------------------------------

BUTTON_RESTART = 17     # Short press = restart synth, Long press = shutdown
BUTTON_NEXT_INST = 27   # Next instrument (hold = reset to core piano)
BUTTON_PREV_INST = 22   # Previous instrument

LED_RED = 24            # Single status LED (solid=ready, blink=shutting down)

# ---------------------------------------------------------------------------
# Button Timing
# ---------------------------------------------------------------------------

LONG_PRESS_SECONDS = 3.0
RESET_HOLD_SECONDS = 1.0
DEBOUNCE_SECONDS = 0.05

# ---------------------------------------------------------------------------
# FluidSynth Settings (tuned for Raspberry Pi 3)
# ---------------------------------------------------------------------------

SOUNDFONT_PATH = "/home/pi/piano-pi-brain/soundfonts/SalamanderGrandPiano.sf2"
SOUNDFONT_FALLBACK = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

FLUIDSYNTH_CMD = [
    "fluidsynth",
    "-a", "alsa",
    "-m", "alsa_seq",
    "-r", "44100",
    "-c", "3",
    "-z", "128",
    "-g", "1.0",
    "-o", "synth.polyphony=64",
    "-o", "synth.cpu-cores=4",
    "-C0",
    "-R0",
]

# ---------------------------------------------------------------------------
# Instruments (General MIDI program numbers)
# Core 3 = hold Next button to reset to #1
# ---------------------------------------------------------------------------

INSTRUMENTS = [
    # --- Core 3 ---
    {"name": "Grand Piano",            "program": 0,  "core": True},
    {"name": "Clavinet",               "program": 7,  "core": True},
    {"name": "Strings Ensemble",       "program": 48, "core": True},
    # --- Extras ---
    {"name": "Electric Grand Piano",   "program": 2},
    {"name": "Acoustic Guitar Nylon",  "program": 24},
    {"name": "Rhodes Piano",           "program": 4},
    {"name": "Rock Organ",             "program": 18},
    {"name": "Overdriven Guitar",      "program": 29},
    {"name": "Synth Pad (warm)",       "program": 89},
]

DEFAULT_INSTRUMENT_INDEX = 0

# ---------------------------------------------------------------------------
# MIDI Settings
# ---------------------------------------------------------------------------

# All MIDI channels to apply instrument changes to
# Keystation 49 MK3 = ch 4, Arturia MiniLab 3 = ch 0
MIDI_CHANNELS = [0, 4]

MIDI_POLL_INTERVAL = 2.0
