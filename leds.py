"""
Piano Pi Brain — LED Status (Simplified)

Single red LED on GPIO 24:
  - Solid = ready (FluidSynth running)
  - Blinking = shutting down (safe to unplug when LED turns off)
"""

import logging
from enum import Enum, auto

try:
    from gpiozero import LED
except ImportError:
    LED = None

import config

log = logging.getLogger(__name__)


class State(Enum):
    OFF = auto()
    STARTING = auto()
    READY = auto()
    READY_NO_MIDI = auto()
    SHUTTING_DOWN = auto()
    ERROR = auto()


class StatusLEDs:
    """Single LED status indicator."""

    def __init__(self):
        if LED is None:
            log.warning("gpiozero not available — LED disabled (dev mode)")
            self._enabled = False
            return

        self._enabled = True
        self.led = LED(config.LED_RED)
        self._state = State.OFF
        self.led.off()

    def set_state(self, state: State):
        if not self._enabled:
            log.info(f"LED state -> {state.name}")
            return

        if state == self._state:
            return

        self.led.off()
        self._state = state

        if state in (State.READY, State.READY_NO_MIDI):
            self.led.on()
        elif state == State.STARTING:
            self.led.blink(on_time=0.3, off_time=0.3)
        elif state == State.SHUTTING_DOWN:
            self.led.blink(on_time=0.1, off_time=0.1)
        elif state == State.ERROR:
            self.led.blink(on_time=0.8, off_time=0.2)

        log.info(f"LED state -> {state.name}")

    def cleanup(self):
        if not self._enabled:
            return
        self.led.off()
        self.led.close()
