"""
Piano Pi Brain — Button Handler

Manages 3 breadboard buttons via gpiozero:
  - Button 1: Short press = restart synth, Long press (3s) = safe shutdown
  - Button 2: Next instrument
  - Button 3: Previous instrument
"""

import logging
import os
import time
import threading

try:
    from gpiozero import Button
except ImportError:
    Button = None

import config

log = logging.getLogger(__name__)


class ButtonHandler:
    """Manages physical buttons and dispatches actions."""

    def __init__(self, on_restart=None, on_shutdown=None,
                 on_next_instrument=None, on_prev_instrument=None):
        """
        Args:
            on_restart: Callback when short-press on button 1
            on_shutdown: Callback when long-press on button 1
            on_next_instrument: Callback when button 2 pressed
            on_prev_instrument: Callback when button 3 pressed
        """
        self._on_restart = on_restart
        self._on_shutdown = on_shutdown
        self._on_next = on_next_instrument
        self._on_prev = on_prev_instrument
        self._press_time = None  # Track when button 1 was pressed

        if Button is None:
            log.warning("gpiozero not available — buttons disabled (dev mode)")
            self._enabled = False
            return

        self._enabled = True

        # Button 1: restart / shutdown (uses press + release for long-press detection)
        self.btn_restart = Button(
            config.BUTTON_RESTART,
            pull_up=True,
            bounce_time=config.DEBOUNCE_SECONDS,
        )
        self.btn_restart.when_pressed = self._on_btn1_pressed
        self.btn_restart.when_released = self._on_btn1_released

        # Button 2: next instrument
        self.btn_next = Button(
            config.BUTTON_NEXT_INST,
            pull_up=True,
            bounce_time=config.DEBOUNCE_SECONDS,
        )
        self.btn_next.when_pressed = self._on_btn2_pressed

        # Button 3: previous instrument
        self.btn_prev = Button(
            config.BUTTON_PREV_INST,
            pull_up=True,
            bounce_time=config.DEBOUNCE_SECONDS,
        )
        self.btn_prev.when_pressed = self._on_btn3_pressed

        log.info("Buttons initialized (pins %d, %d, %d)",
                 config.BUTTON_RESTART, config.BUTTON_NEXT_INST, config.BUTTON_PREV_INST)

    def _on_btn1_pressed(self):
        """Record when button 1 was pressed."""
        self._press_time = time.monotonic()

    def _on_btn1_released(self):
        """On release, decide short press vs long press."""
        if self._press_time is None:
            return

        held = time.monotonic() - self._press_time
        self._press_time = None

        if held >= config.LONG_PRESS_SECONDS:
            log.info("Button 1: LONG press (%.1fs) -> shutdown", held)
            if self._on_shutdown:
                self._on_shutdown()
        else:
            log.info("Button 1: SHORT press (%.1fs) -> restart synth", held)
            if self._on_restart:
                self._on_restart()

    def _on_btn2_pressed(self):
        """Button 2 pressed -> next instrument."""
        log.info("Button 2: next instrument")
        if self._on_next:
            self._on_next()

    def _on_btn3_pressed(self):
        """Button 3 pressed -> previous instrument."""
        log.info("Button 3: previous instrument")
        if self._on_prev:
            self._on_prev()

    def cleanup(self):
        """Release GPIO resources."""
        if not self._enabled:
            return
        self.btn_restart.close()
        self.btn_next.close()
        self.btn_prev.close()
