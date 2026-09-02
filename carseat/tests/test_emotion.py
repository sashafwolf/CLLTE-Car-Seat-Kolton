import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from carseat.emotion import determine_emotional_state


def test_calm_when_steady_and_neutral():
    assert determine_emotional_state("I want to go to the store", 2.0) == "Calm"


def test_stuck_when_slow_and_loud():
    assert determine_emotional_state("I I I the the", 5.0, volume_spike=True) == "Stuck"


def test_frustrated_on_negative_sentiment():
    assert determine_emotional_state("Why is this so hard", 2.0) == "Frustrated"


def test_frustrated_on_cant():
    assert determine_emotional_state("I can't do this", 2.0) == "Frustrated"


from carseat.emotion import VolumeSpikeDetector


def test_detector_goes_loud_and_stays_until_quiet():
    d = VolumeSpikeDetector(high=3000, low=1500)
    assert d.update(100) is False
    assert d.update(5000) is True      # loud burst -> spike
    assert d.update(2500) is True      # between thresholds -> stays (hysteresis)
    assert d.update(1000) is False     # quiet -> clears
