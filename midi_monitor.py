"""
Piano Pi Brain — MIDI Monitor

Watches for USB MIDI controllers connecting/disconnecting.
Auto-connects new MIDI devices to FluidSynth via aconnect.
"""

import logging
import re
import subprocess
import threading
import time

import config

log = logging.getLogger(__name__)

# FluidSynth's ALSA sequencer client name
FLUIDSYNTH_CLIENT = "FLUID Synth"


def list_midi_clients() -> list[dict]:
    """
    Parse `aconnect -l` output to find MIDI input clients.
    Returns list of {"id": "20", "name": "MPK mini 3"} dicts.

    We skip system clients (id 0 = System, id 14 = Midi Through)
    and FluidSynth itself.
    """
    try:
        result = subprocess.run(
            ["aconnect", "-l"],
            capture_output=True, text=True, timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    clients = []
    for line in result.stdout.splitlines():
        # Lines look like: "client 20: 'MPK mini 3' [type=kernel,card=1]"
        match = re.match(r"^client\s+(\d+):\s+'(.+?)'\s+\[(.+?)\]", line)
        if not match:
            continue

        client_id = match.group(1)
        client_name = match.group(2)
        client_info = match.group(3)

        # Skip system ports and FluidSynth itself
        if int(client_id) in (0, 14):
            continue
        if FLUIDSYNTH_CLIENT in client_name:
            continue

        clients.append({"id": client_id, "name": client_name})

    return clients


def find_fluidsynth_port() -> str | None:
    """Find FluidSynth's ALSA sequencer client ID."""
    try:
        result = subprocess.run(
            ["aconnect", "-l"],
            capture_output=True, text=True, timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    for line in result.stdout.splitlines():
        match = re.match(r"^client\s+(\d+):\s+'(.+?)'", line)
        if match and FLUIDSYNTH_CLIENT in match.group(2):
            return match.group(1)
    return None


def connect_midi(source_id: str, dest_id: str) -> bool:
    """Connect a MIDI source to a destination via aconnect."""
    try:
        result = subprocess.run(
            ["aconnect", f"{source_id}:0", f"{dest_id}:0"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            log.info("Connected MIDI %s:0 -> %s:0", source_id, dest_id)
            return True
        else:
            log.warning("aconnect failed: %s", result.stderr.strip())
            return False
    except Exception as e:
        log.error("aconnect error: %s", e)
        return False


class MidiMonitor:
    """Polls for MIDI devices and auto-connects them to FluidSynth."""

    def __init__(self, on_midi_connected=None, on_midi_disconnected=None):
        """
        Args:
            on_midi_connected: Callback(name: str) when a MIDI device is connected
            on_midi_disconnected: Callback() when all MIDI devices disconnect
        """
        self._on_connected = on_midi_connected
        self._on_disconnected = on_midi_disconnected
        self._connected_ids: set[str] = set()
        self._thread = None
        self._running = False

    @property
    def has_midi(self) -> bool:
        """True if at least one MIDI controller is connected."""
        return len(self._connected_ids) > 0

    def start(self):
        """Start background polling thread."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        log.info("MIDI monitor started (polling every %.1fs)", config.MIDI_POLL_INTERVAL)

    def stop(self):
        """Stop the polling thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def connect_all(self):
        """Try to connect all detected MIDI devices to FluidSynth now."""
        fs_port = find_fluidsynth_port()
        if not fs_port:
            log.warning("FluidSynth not found in aconnect — can't connect MIDI")
            return

        clients = list_midi_clients()
        for client in clients:
            if client["id"] not in self._connected_ids:
                if connect_midi(client["id"], fs_port):
                    self._connected_ids.add(client["id"])
                    log.info("MIDI controller connected: %s", client["name"])
                    if self._on_connected:
                        self._on_connected(client["name"])

    def _poll_loop(self):
        """Background loop: detect plug/unplug events."""
        while self._running:
            try:
                self._poll_once()
            except Exception as e:
                log.error("MIDI poll error: %s", e)
            time.sleep(config.MIDI_POLL_INTERVAL)

    def _poll_once(self):
        """Check for new or removed MIDI devices."""
        current_clients = list_midi_clients()
        current_ids = {c["id"] for c in current_clients}

        # Detect new devices
        new_ids = current_ids - self._connected_ids
        if new_ids:
            fs_port = find_fluidsynth_port()
            if fs_port:
                for client in current_clients:
                    if client["id"] in new_ids:
                        if connect_midi(client["id"], fs_port):
                            self._connected_ids.add(client["id"])
                            log.info("MIDI hotplug: %s", client["name"])
                            if self._on_connected:
                                self._on_connected(client["name"])

        # Detect removed devices
        removed_ids = self._connected_ids - current_ids
        if removed_ids:
            self._connected_ids -= removed_ids
            log.info("MIDI device(s) removed: %s", removed_ids)
            if not self._connected_ids and self._on_disconnected:
                self._on_disconnected()
