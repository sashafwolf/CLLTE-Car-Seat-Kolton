"""Emotional heuristics engine — turns cadence + sentiment into a state.

Kept deliberately lightweight: no heavy audio-emotion model. It reads the
*text* (VADER sentiment) and the *rhythm* (words-per-second + volume spike)
to pick Calm / Stuck / Frustrated, which the prediction prompt then adapts to.
"""
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    _analyzer = SentimentIntensityAnalyzer()
    _HAS_VADER = True
except Exception:
    _analyzer = None
    _HAS_VADER = False


def _words_per_second(partial_text, time_elapsed):
    if time_elapsed <= 0:
        return 0.0
    return len(partial_text.split()) / time_elapsed


def determine_emotional_state(partial_text, time_elapsed, volume_spike=False):
    """Return one of: Calm, Stuck, Frustrated."""
    wps = _words_per_second(partial_text, time_elapsed)
    compound = 0.0
    if _HAS_VADER and _analyzer is not None:
        try:
            compound = _analyzer.polarity_scores(partial_text)["compound"]
        except Exception:
            compound = 0.0
    low = partial_text.lower()
    if wps <= 1.0 and volume_spike:
        return "Stuck"
    if compound <= -0.1 or "can't" in low or "cant" in low or "why" in low:
        return "Frustrated"
    return "Calm"


class VolumeSpikeDetector:
    """Hysteresis-based loudness detector.

    volume_spike is True while the mic is loud (effort/tension during a
    block) and only clears once volume drops back below a lower threshold.
    This avoids flickering on a single loud frame.
    """

    def __init__(self, high=3000.0, low=1500.0):
        self.high = high
        self.low = low
        self.spike = False

    def update(self, level):
        if level > self.high:
            self.spike = True
        elif level < self.low:
            self.spike = False
        return self.spike
