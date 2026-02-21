"""
Piano Pi Brain — Web Portal

Lightweight Flask server for phone-based control.
Runs in a background thread inside piano_pi.py.

API:
  GET  /                    → Mobile UI
  GET  /api/state           → Current state (JSON)
  POST /api/instrument/<n>  → Select instrument by index
  POST /api/restart         → Restart FluidSynth
  POST /api/shutdown        → Safe OS shutdown
  GET  /api/events          → SSE stream for real-time updates
"""

import json
import logging
import queue
import threading

from flask import Flask, Response, jsonify, send_from_directory

log = logging.getLogger(__name__)

# Global event queues for SSE clients
_sse_clients: list[queue.Queue] = []
_sse_lock = threading.Lock()


def create_app(synth, midi, leds, restart_cb, shutdown_cb):
    """
    Create the Flask app with references to the running components.

    Args:
        synth: FluidSynthManager instance
        midi: MidiMonitor instance
        leds: StatusLEDs instance
        restart_cb: Callable for restarting FluidSynth
        shutdown_cb: Callable for safe shutdown
    """
    import config

    app = Flask(__name__, static_folder=None)
    app.logger.setLevel(logging.WARNING)  # Suppress Flask's request logs

    # Disable Flask's default logging to keep our logs clean
    werkzeug_log = logging.getLogger("werkzeug")
    werkzeug_log.setLevel(logging.WARNING)

    # ---------------------------------------------------------------
    # Static files (serve from web/ directory)
    # ---------------------------------------------------------------

    @app.route("/")
    def index():
        return send_from_directory("web", "index.html")

    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory("web/static", filename)

    # ---------------------------------------------------------------
    # REST API
    # ---------------------------------------------------------------

    @app.route("/api/state")
    def get_state():
        """Return current state as JSON."""
        instruments = []
        for i, inst in enumerate(config.INSTRUMENTS):
            instruments.append({
                "index": i,
                "name": inst["name"],
                "program": inst["program"],
                "core": inst.get("core", False),
                "active": i == synth._current_instrument_index,
            })

        return jsonify({
            "instrument": synth.get_current_instrument(),
            "instrument_index": synth._current_instrument_index,
            "instruments": instruments,
            "synth_running": synth.is_running,
            "midi_connected": midi.has_midi,
        })

    @app.route("/api/instrument/<int:index>", methods=["POST"])
    def select_instrument(index):
        """Select an instrument by index."""
        if index < 0 or index >= len(config.INSTRUMENTS):
            return jsonify({"error": "Invalid instrument index"}), 400

        synth._current_instrument_index = index
        name = synth._apply_instrument()
        log.info("🌐 Web: instrument -> %s", name)

        broadcast_event("instrument", {
            "name": name,
            "index": index,
        })

        return jsonify({"instrument": name, "index": index})

    @app.route("/api/restart", methods=["POST"])
    def restart():
        """Restart FluidSynth."""
        log.info("🌐 Web: restart requested")
        threading.Thread(target=restart_cb, daemon=True).start()
        return jsonify({"status": "restarting"})

    @app.route("/api/shutdown", methods=["POST"])
    def shutdown():
        """Safe OS shutdown."""
        log.info("🌐 Web: shutdown requested")
        threading.Thread(target=shutdown_cb, daemon=True).start()
        return jsonify({"status": "shutting_down"})

    # ---------------------------------------------------------------
    # Server-Sent Events (SSE) for real-time updates
    # ---------------------------------------------------------------

    @app.route("/api/events")
    def sse_stream():
        """SSE endpoint — clients receive real-time state changes."""
        q = queue.Queue(maxsize=50)
        with _sse_lock:
            _sse_clients.append(q)

        def generate():
            try:
                while True:
                    try:
                        data = q.get(timeout=30)
                        yield f"data: {json.dumps(data)}\n\n"
                    except queue.Empty:
                        # Send keepalive to prevent connection timeout
                        yield ": keepalive\n\n"
            finally:
                with _sse_lock:
                    if q in _sse_clients:
                        _sse_clients.remove(q)

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return app


def broadcast_event(event_type: str, data: dict):
    """Send an event to all connected SSE clients."""
    payload = {"type": event_type, **data}
    with _sse_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)


def start_server(app, host="0.0.0.0", port=8080):
    """Start Flask in a background thread."""
    def run():
        app.run(host=host, port=port, threaded=True, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    log.info("🌐 Web portal running at http://%s:%d", host, port)
    return thread
