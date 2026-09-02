"""CLLTE Car Seat — configuration & secrets loading.

Everything secret comes from environment variables (or a local .env),
never hardcoded. See .env.example for the full list.
"""
import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


# Load .env from the carseat package dir, then the repo root.
_load_dotenv(Path(__file__).resolve().parent / ".env")
_load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# --- Required secrets (empty until Kolton's .env is filled) ---
ELEVENLABS_API_KEY = get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = get("ELEVENLABS_VOICE_ID", "koltons_collette_voice_id")
ELEVENLABS_MODEL = get("ELEVENLABS_MODEL", "eleven_turbo_v2_5")
OPENROUTER_API_KEY = get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
GEMINI_API_KEY = get("GEMINI_API_KEY")

# --- Tuning knobs ---
HOST = get("CARSEAT_HOST", "127.0.0.1")
PORT = int(get("CARSEAT_PORT", "8001"))
STT_MODEL = get("CARSEAT_STT_MODEL", "medium")
STT_DEVICE = get("CARSEAT_STT_DEVICE", "cuda")
STT_COMPUTE = get("CARSEAT_STT_COMPUTE", "float16")
CHUNK_EVERY = int(get("CARSEAT_CHUNK_EVERY", "3"))        # 500ms chunks before STT
GRACE_SECONDS = float(get("CARSEAT_GRACE_SECONDS", "2.0"))  # 2s grace buffer
AUTO_SLEEP_SECONDS = float(get("CARSEAT_AUTO_SLEEP_SECONDS", "180.0"))
MAX_PREDICT_WORDS = int(get("CARSEAT_MAX_PREDICT_WORDS", "5"))
VOLUME_HIGH = float(get("CARSEAT_VOLUME_HIGH", "3000"))
VOLUME_LOW = float(get("CARSEAT_VOLUME_LOW", "1500"))
