"""ElevenLabs WebSocket streaming TTS — pipes predicted words to audio.

Uses the stream-input endpoint so audio starts flowing before the whole
prediction is done, and supports an abort callback (F7 kill switch).
"""
import asyncio
import json

import websockets

from . import config


async def stream_to_elevenlabs(predicted_text_generator, on_audio, should_abort=None):
    """Open a persistent ElevenLabs stream-input socket.

    predicted_text_generator: sync or async generator of text chunks.
    on_audio(b64): callback receiving base64 audio chunks.
    should_abort(): optional callable returning True to stop early.
    """
    if not config.ELEVENLABS_API_KEY:
        # No key configured — just drain the generator (demo mode).
        async for _ in _aiter(predicted_text_generator):
            pass
        return

    uri = (
        f"wss://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
        f"/stream-input?model_id={config.ELEVENLABS_MODEL}"
    )
    async with websockets.connect(
        uri, additional_headers={"xi-api-key": config.ELEVENLABS_API_KEY}
    ) as ws:
        await ws.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }))

        async def send_text():
            async for text_chunk in _aiter(predicted_text_generator):
                if should_abort and should_abort():
                    break
                await ws.send(json.dumps({
                    "text": text_chunk,
                    "try_trigger_generation": True,
                }))
            await ws.send(json.dumps({"text": ""}))

        async def receive_audio():
            async for message in ws:
                if should_abort and should_abort():
                    break
                try:
                    response = json.loads(message)
                except Exception:
                    continue
                if response.get("audio"):
                    on_audio(response["audio"])
                if response.get("isFinal"):
                    break

        await asyncio.gather(send_text(), receive_audio())


async def _aiter(gen):
    """Yield from a sync or async generator."""
    if hasattr(gen, "__aiter__"):
        async for item in gen:
            yield item
    else:
        for item in gen:
            yield item

