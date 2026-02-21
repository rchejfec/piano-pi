#!/usr/bin/env python3
"""
Piano Pi Brain — Main Orchestrator

Entry point that ties everything together:
  1. Initialize LEDs (yellow = starting)
  2. Start FluidSynth
  3. Start MIDI monitor (auto-connect controllers)
  4. Initialize buttons
  5. Green LED = ready, sit in main loop

Usage:
    python3 piano_pi.py
"""

import logging
import os
import signal
import subprocess
import sys
import time

from leds import StatusLEDs, State
from synth import FluidSynthManager
from midi_monitor import MidiMonitor
from buttons import ButtonHandler

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("piano-pi")

# ---------------------------------------------------------------------------
# Globals (needed for signal handler)
# ---------------------------------------------------------------------------

leds: StatusLEDs = None
synth: FluidSynthManager = None
midi: MidiMonitor = None
buttons: ButtonHandler = None


def main():
    global leds, synth, midi, buttons

    log.info("=" * 50)
    log.info("  Piano Pi Brain — Starting up")
    log.info("=" * 50)

    # --- LEDs ---
    leds = StatusLEDs()
    leds.set_state(State.STARTING)

    # --- FluidSynth ---
    synth = FluidSynthManager()

    if not synth.start():
        log.error("Failed to start FluidSynth!")
        leds.set_state(State.ERROR)
        # Keep running so buttons still work for restart
    else:
        log.info("FluidSynth started — instrument: %s", synth.get_current_instrument())

    # --- MIDI Monitor ---
    midi = MidiMonitor(
        on_midi_connected=on_midi_connected,
        on_midi_disconnected=on_midi_disconnected,
    )
    # Try to connect any already-plugged-in controllers
    midi.connect_all()
    midi.start()

    # Update LED based on MIDI state
    if synth.is_running:
        if midi.has_midi:
            leds.set_state(State.READY)
        else:
            leds.set_state(State.READY_NO_MIDI)

    # --- Buttons ---
    buttons = ButtonHandler(
        on_restart=on_restart,
        on_shutdown=on_shutdown,
        on_next_instrument=on_next_instrument,
        on_prev_instrument=on_prev_instrument,
        on_reset_instrument=on_reset_instrument,
    )

    # --- Signal handlers for clean exit ---
    signal.signal(signal.SIGTERM, shutdown_signal)
    signal.signal(signal.SIGINT, shutdown_signal)

    log.info("Ready! Waiting for input...")

    # --- Main loop: just keep alive, everything is event-driven ---
    try:
        while True:
            # Periodic health check on FluidSynth
            if not synth.is_running:
                log.warning("FluidSynth died — auto-restarting...")
                leds.set_state(State.STARTING)
                if synth.restart():
                    midi.connect_all()
                    update_led_state()
                else:
                    leds.set_state(State.ERROR)

            time.sleep(5)

    except KeyboardInterrupt:
        log.info("Keyboard interrupt — shutting down")
        cleanup()


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

def on_midi_connected(name: str):
    """Called when a MIDI controller is plugged in."""
    log.info("🎹 MIDI connected: %s", name)
    if synth.is_running:
        leds.set_state(State.READY)


def on_midi_disconnected():
    """Called when all MIDI controllers are unplugged."""
    log.info("🎹 MIDI disconnected")
    if synth.is_running:
        leds.set_state(State.READY_NO_MIDI)


def on_restart():
    """Button 1 short press — restart FluidSynth."""
    log.info("🔄 Restarting FluidSynth...")
    leds.set_state(State.STARTING)

    if synth.restart():
        # Re-connect MIDI devices after restart
        time.sleep(1)
        midi.connect_all()
        update_led_state()
        log.info("✅ Restart complete — instrument: %s", synth.get_current_instrument())
    else:
        leds.set_state(State.ERROR)
        log.error("❌ Restart failed!")


def on_shutdown():
    """Button 1 long press — safe OS shutdown."""
    log.info("⏻ Shutdown requested — powering off...")
    cleanup()
    leds_shutdown = StatusLEDs()
    leds_shutdown.set_state(State.SHUTTING_DOWN)
    subprocess.run(["sudo", "shutdown", "-h", "now"])


def on_next_instrument():
    """Button 2 short press — next instrument."""
    name = synth.next_instrument()
    log.info("🎵 Next instrument: %s", name)


def on_prev_instrument():
    """Button 3 — previous instrument."""
    name = synth.prev_instrument()
    log.info("🎵 Previous instrument: %s", name)


def on_reset_instrument():
    """Button 2 hold — reset to core piano (instrument 0)."""
    name = synth.reset_instrument()
    log.info("🎹 Reset to core: %s", name)


def update_led_state():
    """Set LED based on current synth + MIDI state."""
    if not synth.is_running:
        leds.set_state(State.ERROR)
    elif midi.has_midi:
        leds.set_state(State.READY)
    else:
        leds.set_state(State.READY_NO_MIDI)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def shutdown_signal(signum, frame):
    """Handle SIGTERM/SIGINT."""
    log.info("Received signal %d — shutting down", signum)
    cleanup()
    sys.exit(0)


def cleanup():
    """Stop everything gracefully."""
    log.info("Cleaning up...")
    if midi:
        midi.stop()
    if synth:
        synth.stop()
    if buttons:
        buttons.cleanup()
    if leds:
        leds.cleanup()
    log.info("Cleanup complete")


if __name__ == "__main__":
    main()
