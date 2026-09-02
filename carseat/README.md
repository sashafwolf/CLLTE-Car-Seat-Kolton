# CLLTE Car Seat — Shadow & Predict engine (Project SOAR)

A lightweight, real-time speech shadow and predictive echolalia companion
for Kolton. It listens continuously, predicts the next few words he is
trying to say, and speaks them back through ElevenLabs — adapting its style
to whether he is calm, stuck, or frustrated.

## The loop

Kolton speaks -> browser chunks the mic (500ms) & monitors volume ->
Python accumulates bytes -> faster-whisper transcribes -> emotional state
is detected (cadence + sentiment) -> OpenRouter predicts the next words ->
ElevenLabs streams the audio back -> browser plays it in order.

## Controls

- **F7** — kill switch. Stops Collette instantly and lets him finish.
- **Silence (1.2s)** — sends `speech_ended`, resetting the buffer.
- **Auto-sleep (3 min)** — stops the mic if no speech is heard, to protect
  API budget (the "Money Law").
- **Echo guard** — the backend ignores mic chunks while she is speaking.

## Run it

1. `copy .env.example .env` and fill in the real API keys (ElevenLabs,
   OpenRouter). Never commit `.env`.
2. Install deps: `pip install flask flask-socketio websockets faster-whisper`
   (plus `nltk` for sentiment, or it degrades gracefully).
3. `python -m carseat.server`  ->  open http://127.0.0.1:8001

## Volume spike (stuck detection)

The frontend reports raw mic volume; the backend runs a hysteresis detector
(CARSEAT_VOLUME_HIGH / CARSEAT_VOLUME_LOW) so a loud effort burst during a
block flips the emotion engine to Stuck and triggers the echolalia anchor.

## Tests

`python -m pytest carseat/tests` (pure-logic core only; no server needed).

