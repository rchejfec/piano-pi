"""
Piano Pi Brain — FluidSynth Manager

Manages FluidSynth as a subprocess:
  - Start/stop/restart
  - Instrument switching on all configured MIDI channels
"""

import logging
import os
import subprocess
import time

import config

log = logging.getLogger(__name__)


class FluidSynthManager:
    """Wraps FluidSynth as a managed subprocess."""

    def __init__(self, on_state_change=None):
        self._process = None
        self._on_state_change = on_state_change
        self._current_instrument_index = config.DEFAULT_INSTRUMENT_INDEX

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> bool:
        """Start FluidSynth."""
        if self.is_running:
            return True

        # Try primary soundfont, fall back to GM
        if os.path.isfile(config.SOUNDFONT_PATH):
            soundfont = config.SOUNDFONT_PATH
        elif hasattr(config, 'SOUNDFONT_FALLBACK') and os.path.isfile(config.SOUNDFONT_FALLBACK):
            log.warning("Primary SoundFont not found, using fallback: %s", config.SOUNDFONT_FALLBACK)
            soundfont = config.SOUNDFONT_FALLBACK
        else:
            log.error("No SoundFont found!")
            return False

        cmd = config.FLUIDSYNTH_CMD + [soundfont]
        log.info("Starting FluidSynth: %s", " ".join(cmd))

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            time.sleep(3)

            if self._process.poll() is not None:
                stderr = self._process.stderr.read().decode(errors="replace")
                log.error("FluidSynth exited immediately: %s", stderr)
                self._process = None
                return False

            log.info("FluidSynth started (pid %d)", self._process.pid)
            self._process.stderr.close()

            # Set the default instrument on all channels
            self._apply_instrument()

            if self._on_state_change:
                self._on_state_change("running")

            return True

        except Exception as e:
            log.error("Failed to start FluidSynth: %s", e)
            self._process = None
            return False

    def stop(self):
        """Stop FluidSynth gracefully."""
        if self._process is None:
            return

        log.info("Stopping FluidSynth (pid %d)", self._process.pid)

        try:
            self._send_command("quit")
            self._process.wait(timeout=5)
        except Exception:
            try:
                self._process.terminate()
                self._process.wait(timeout=3)
            except Exception:
                self._process.kill()

        self._process = None
        log.info("FluidSynth stopped")

        if self._on_state_change:
            self._on_state_change("stopped")

    def restart(self):
        """Stop then start FluidSynth."""
        log.info("Restarting FluidSynth...")
        self.stop()
        time.sleep(0.5)
        return self.start()

    def next_instrument(self) -> str:
        self._current_instrument_index = (
            (self._current_instrument_index + 1) % len(config.INSTRUMENTS)
        )
        return self._apply_instrument()

    def prev_instrument(self) -> str:
        self._current_instrument_index = (
            (self._current_instrument_index - 1) % len(config.INSTRUMENTS)
        )
        return self._apply_instrument()

    def reset_instrument(self) -> str:
        self._current_instrument_index = 0
        return self._apply_instrument()

    def get_current_instrument(self) -> str:
        return config.INSTRUMENTS[self._current_instrument_index]["name"]

    def _apply_instrument(self) -> str:
        """Send program change on ALL configured MIDI channels."""
        inst = config.INSTRUMENTS[self._current_instrument_index]
        log.info("Instrument -> %s (program %d)", inst["name"], inst["program"])

        for ch in config.MIDI_CHANNELS:
            self._send_command(f"select {ch} 1 0 {inst['program']}")

        return inst["name"]

    def _send_command(self, command: str):
        if not self.is_running:
            log.warning("Cannot send command — FluidSynth not running")
            return

        try:
            self._process.stdin.write(f"{command}\n".encode())
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            log.error("Failed to send command to FluidSynth: %s", e)

    def cleanup(self):
        self.stop()
