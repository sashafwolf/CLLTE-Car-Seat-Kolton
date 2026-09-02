"""Predictive LLM core — strict sentence-completion, no filler.

The model is told to forget it is a chatbot. It only completes the next
3-5 words, and adapts its style to the detected emotional state (echolalia
anchor when stuck/frustrated).
"""
import json
import urllib.request

from . import config

SYSTEM_PROMPT = """You are a real-time speech prediction engine assisting a user who has a stutter.
You will receive a continuous stream of partial, incomplete sentences.
Your ONLY objective is to predict the next 3 to 5 words the user is trying to say.

STRICT RULES:
1. Output ONLY the exact predicted words. Absolutely zero conversational filler, greetings, or acknowledgments.
2. DO NOT repeat the words the user has already spoken.
3. DO NOT output punctuation (periods, commas, question marks). It will cause unnatural pauses in the downstream Text-to-Speech engine.
4. Keep predictions to {max_words} words maximum.
5. If the input sentence appears grammatically complete, output nothing (an empty string).

STATE BEHAVIORS:
- If [STATE: Calm], predict the next 3-5 words seamlessly to help him finish his thought.
- If [STATE: Stuck/Frustrated], do NOT just predict the end of the sentence. Instead, provide a gentle, rhythmic 2-3 word anchor that repeats his last concept to help him reset (echolalia), or a short validating completion.

EXAMPLES:
Input: [STATE: Calm] "I am trying to find my"
Output: keys before we leave

Input: [STATE: Calm] "Can we go to the"
Output: store to get some

Input: [STATE: Stuck] "I... I can't... the the"
Output: take your time

Input: [STATE: Frustrated] "Why is this so"
Output: hard right now, I know

Input: [STATE: Calm] "I'm hungry let's eat"
Output:
"""


def build_messages(partial_text, state="Calm"):
    user = f'Input: [STATE: {state}] "{partial_text}"\nOutput:'
    return [
        {"role": "system", "content": SYSTEM_PROMPT.format(max_words=config.MAX_PREDICT_WORDS)},
        {"role": "user", "content": user},
    ]


def _openrouter_stream(messages):
    """Yield predicted text chunks from OpenRouter (Luna)."""
    body = {
        "model": config.OPENROUTER_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                delta = json.loads(payload)["choices"][0]["delta"].get("content", "")
            except Exception:
                delta = ""
            if delta:
                yield delta


def predict_speech(partial_text, state="Calm"):
    """Generator yielding predicted words. Empty if nothing to say."""
    if not partial_text or not partial_text.strip():
        return
    messages = build_messages(partial_text, state)
    if not config.OPENROUTER_API_KEY:
        # Offline fallback: a gentle deterministic anchor so the loop still demos.
        yield _offline_fallback(partial_text)
        return
    for chunk in _openrouter_stream(messages):
        yield chunk


def _offline_fallback(partial_text):
    """Deterministic stand-in when no API key is configured (demo mode)."""
    words = partial_text.strip().split()
    last = words[-1] if words else ""
    return f" {last} ..."
