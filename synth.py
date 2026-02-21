"""
Piano Pi Brain — FluidSynth Manager

Manages FluidSynth as a subprocess: start, stop, restart, instrument changes.
Communicates with FluidSynth via its FIFO command interface.
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
        """
        Args:
            on_state_change: Callback(running: bool) called when synth starts/stops.
        """
        self._process = None
        self._on_state_change = on_state_change
        self._current_instrument_index = config.DEFAULT_INSTRUMENT_INDEX

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> bool:
        """Start FluidSynth. Returns True on success."""
        if self.is_running:
            log.warning("FluidSynth already running (pid %d)", self._process.pid)
            return True

        if not os.path.isfile(config.SOUNDFONT_PATH):
            if hasattr(config, 'SOUNDFONT_FALLBACK') and os.path.isfile(config.SOUNDFONT_FALLBACK):
                log.warning("Primary SoundFont not found, using fallback: %s", config.SOUNDFONT_FALLBACK)
                soundfont = config.SOUNDFONT_FALLBACK
            else:
                log.error("No SoundFont found!")
                return False
        else:
            soundfont = config.SOUNDFONT_PATH

        cmd = config.FLUIDSYNTH_CMD + [soundfont]
        log.info("Starting FluidSynth: %s", " ".join(cmd))

        try:
            # stderr to PIPE so we can read it if startup fails,
            # stdout to DEVNULL to prevent pipe buffer fill-up
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            # Give it a moment to initialize
            time.sleep(3)

            if self._process.poll() is not None:
                stderr = self._process.stderr.read().decode(errors="replace")
                log.error("FluidSynth exited immediately: %s", stderr)
                self._process = None
                return False

            log.info("FluidSynth started (pid %d)", self._process.pid)

            # Close stderr now that startup check passed — prevents pipe buffer fill
            self._process.stderr.close()

            # Set the default instrument on the correct MIDI channel
            self._send_command(
                f"select {config.MIDI_CHANNEL} 1 0 {config.INSTRUMENTS[self._current_instrument_index]['program']}"
            )

            if self._on_state_change:
                self._on_state_change(True)
            return True

        except FileNotFoundError:
            log.error("fluidsynth binary not found — is it installed?")
            return False
        except Exception as e:
            log.error("Failed to start FluidSynth: %s", e)
            return False

    def stop(self):
        """Stop FluidSynth gracefully."""
        if self._process is None:
            return

        log.info("Stopping FluidSynth (pid %d)", self._process.pid)
        try:
            self._send_command("quit")
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            log.warning("FluidSynth didn't quit gracefully, killing")
            self._process.kill()
            self._process.wait()
        except Exception:
            pass
        finally:
            self._process = None
            if self._on_state_change:
                self._on_state_change(False)
            log.info("FluidSynth stopped")

    def restart(self):
        """Stop then start FluidSynth (error recovery)."""
        log.info("Restarting FluidSynth...")
        self.stop()
        time.sleep(0.5)
        return self.start()

    def next_instrument(self) -> str:
        """Switch to the next instrument in the list. Returns the instrument name."""
        self._current_instrument_index = (
            (self._current_instrument_index + 1) % len(config.INSTRUMENTS)
        )
        return self._apply_instrument()

    def prev_instrument(self) -> str:
        """Switch to the previous instrument in the list. Returns the instrument name."""
        self._current_instrument_index = (
            (self._current_instrument_index - 1) % len(config.INSTRUMENTS)
        )
        return self._apply_instrument()

    def reset_instrument(self) -> str:
        """Reset to the first instrument (core piano). Returns the instrument name."""
        self._current_instrument_index = 0
        return self._apply_instrument()

    def get_current_instrument(self) -> str:
        """Return the name of the current instrument."""
        return config.INSTRUMENTS[self._current_instrument_index]["name"]

    def _apply_instrument(self) -> str:
        """Send program change to FluidSynth. Returns instrument name."""
        inst = config.INSTRUMENTS[self._current_instrument_index]
        log.info("Instrument -> %s (program %d)", inst["name"], inst["program"])
        # Use 'select' for explicit soundfont/bank control:
        #   select <chan> <sfont-id> <bank> <program>
        # sfont-id 1 = first loaded soundfont, bank 0 = GM standard
        self._send_command(f"select {config.MIDI_CHANNEL} 1 0 {inst['program']}")
        return inst["name"]

    def _send_command(self, command: str):
        """Send a command to FluidSynth's stdin."""
        if not self.is_running:
            log.warning("Cannot send command — FluidSynth not running")
            return
        try:
            self._process.stdin.write(f"{command}\n".encode())
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            log.error("Failed to send command to FluidSynth: %s", e)
