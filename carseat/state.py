"""Shared per-session state for the Car Seat loop."""
import threading


class CarseatState:
    def __init__(self):
        self.lock = threading.RLock()
        self.audio_buffer = bytearray()
        self.chunk_counter = 0
        self.last_text = ""
        self.is_predicting = False
        self.is_speaking = False      # echo guard: ignore mic while she talks
        self.abort_flag = False
        self.volume_spike = False     # set by the volume event handler
        self.last_activity = 0.0      # monotonic time of last human speech
        self.connected = False

    def reset_buffer(self):
        with self.lock:
            self.audio_buffer = bytearray()
            self.chunk_counter = 0
            self.last_text = ""

    def append(self, data):
        with self.lock:
            self.audio_buffer.extend(data)
            self.chunk_counter += 1

    def snapshot(self):
        with self.lock:
            return bytes(self.audio_buffer), self.chunk_counter, self.last_text

    def set_predicting(self, value):
        with self.lock:
            self.is_predicting = value

    def abort(self):
        with self.lock:
            self.abort_flag = True

    def clear_abort(self):
        with self.lock:
            self.abort_flag = False

    def should_abort(self):
        with self.lock:
            return self.abort_flag
