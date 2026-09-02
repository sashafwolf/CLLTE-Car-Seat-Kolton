"""CLLTE Car Seat — WebSocket server (Shadow & Predict engine).

Kolton speaks -> browser chunks it & monitors volume -> Python accumulates
bytes -> Whisper reads it -> emotional state is detected -> OpenRouter
predicts it -> ElevenLabs streams it back. F7 aborts, speech_ended resets.
"""
import asyncio
import threading
import time

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from . import config
from .state import CarseatState
from .emotion import determine_emotional_state, VolumeSpikeDetector
from .predict import predict_speech
from .stt import transcribe
from .elevenlabs_stream import stream_to_elevenlabs

app = Flask(__name__)
app.config["SECRET_KEY"] = config.get("FLASK_SECRET", "carseat_secret")
socketio = SocketIO(app, cors_allowed_origins="*")

state = CarseatState()
spike_detector = VolumeSpikeDetector(high=config.VOLUME_HIGH, low=config.VOLUME_LOW)


@app.route("/")
def index():
    return render_template("carseat.html")


@socketio.on("connect")
def handle_connect():
    state.connected = True
    state.last_activity = time.monotonic()
    emit("server_status", {"msg": "Connected to Collette Car Seat"})


@socketio.on("disconnect")
def handle_disconnect():
    state.connected = False


@socketio.on("audio_chunk")
def handle_audio(data):
    # Echo guard: ignore mic while she's speaking so she doesn't hear herself.
    if state.is_speaking:
        return
    state.append(data)
    state.last_activity = time.monotonic()
    if state.chunk_counter >= config.CHUNK_EVERY and not state.is_predicting:
        state.set_predicting(True)
        socketio.start_background_task(run_prediction_pipeline)


@socketio.on("volume")
def handle_volume(data):
    """Raw mic volume from the frontend -> hysteresis spike detector."""
    try:
        level = float(data.get("level", 0))
    except (TypeError, ValueError):
        level = 0.0
    state.volume_spike = spike_detector.update(level)


@socketio.on("speech_ended")
def handle_silence():
    state.reset_buffer()
    emit("server_status", {"msg": "Listening..."})


@socketio.on("abort_speech")
def handle_abort():
    state.abort()
    emit("server_status", {"msg": "Stopped (F7)"})


def run_prediction_pipeline():
    audio_bytes, _counter, last_text = state.snapshot()
    try:
        partial_text = transcribe(audio_bytes)
    except Exception as exc:
        print(f"[CAR SEAT STT ERROR]: {exc}")
        partial_text = ""

    if partial_text and partial_text != last_text:
        state.clear_abort()
        # 2-second grace buffer on detected halts (trailing comma/ellipsis).
        if partial_text.strip().endswith((",", "...", "-")):
            time.sleep(config.GRACE_SECONDS)
            if state.should_abort() or state.chunk_counter == 0:
                state.set_predicting(False)
                return
        state.last_text = partial_text
        print(f"[KOLTON]: {partial_text}")

        time_elapsed = config.CHUNK_EVERY * 0.5
        volume_spike = state.volume_spike
        emo = determine_emotional_state(partial_text, time_elapsed, volume_spike)
        print(f"[CAR SEAT STATE]: {emo} (volume_spike={volume_spike})")

        def on_audio(b64):
            socketio.emit("audio_playback", {"audio_b64": b64})

        def should_abort():
            return state.should_abort()

        state.is_speaking = True
        try:
            asyncio.run(stream_to_elevenlabs(
                predict_speech(partial_text, emo), on_audio, should_abort
            ))
        finally:
            state.is_speaking = False
            state.reset_buffer()

    state.set_predicting(False)


def _auto_sleep_loop():
    while True:
        time.sleep(5)
        if state.connected and not state.is_speaking:
            idle = time.monotonic() - state.last_activity
            if idle > config.AUTO_SLEEP_SECONDS:
                socketio.emit("auto_sleep", {"msg": "Sleeping (Click Start to Wake)"})


if __name__ == "__main__":
    threading.Thread(target=_auto_sleep_loop, daemon=True).start()
    socketio.run(app, host=config.HOST, port=config.PORT, debug=False)
