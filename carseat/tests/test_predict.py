import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from carseat import predict


def test_build_messages_has_system_and_user():
    msgs = predict.build_messages("I am trying to find my", "Calm")
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert "speech prediction engine" in msgs[0]["content"]
    assert msgs[1]["role"] == "user"
    assert "[STATE: Calm]" in msgs[1]["content"]
    assert "I am trying to find my" in msgs[1]["content"]


def test_build_messages_injects_state():
    msgs = predict.build_messages("I... I can't... the the", "Stuck")
    assert "[STATE: Stuck]" in msgs[1]["content"]


def test_predict_speech_empty_returns_nothing():
    gen = predict.predict_speech("   ")
    assert list(gen) == []


def test_offline_fallback_returns_anchor():
    out = predict._offline_fallback("I want to go")
    assert "go" in out

