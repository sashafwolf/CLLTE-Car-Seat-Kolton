import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from carseat.state import CarseatState


def test_append_and_snapshot():
    s = CarseatState()
    s.append(b"abc")
    s.append(b"def")
    buf, count, _ = s.snapshot()
    assert buf == b"abcdef"
    assert count == 2


def test_reset_buffer():
    s = CarseatState()
    s.append(b"abc")
    s.reset_buffer()
    buf, count, _ = s.snapshot()
    assert buf == b""
    assert count == 0


def test_abort_flag():
    s = CarseatState()
    assert not s.should_abort()
    s.abort()
    assert s.should_abort()
    s.clear_abort()
    assert not s.should_abort()

