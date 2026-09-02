"""faster-whisper STT — transcribe raw audio bytes via a temp file."""
import os
import tempfile

from . import config

_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(
            config.STT_MODEL,
            device=config.STT_DEVICE,
            compute_type=config.STT_COMPUTE,
        )
    return _whisper_model


def transcribe(audio_bytes):
    """Return the transcript text for raw audio bytes (webm/wav)."""
    if not audio_bytes:
        return ""
    suffix = ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        model = _get_model()
        segments, _info = model.transcribe(tmp, beam_size=1)
        return "".join(seg.text for seg in segments).strip()
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
