import numpy as np

from app.storage.analysis_cache import AnalysisCache


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def make_frames():
    return np.zeros((16, 224, 224, 3), dtype=np.uint8)


def test_returns_a_stored_analysis_by_id():
    cache = AnalysisCache()

    analysis_id = cache.add(make_frames(), list(range(16)), 25.0, 1)

    analysis = cache.get(analysis_id)
    assert analysis is not None
    assert analysis.frame_numbers == list(range(16))
    assert analysis.fps == 25.0


def test_returns_none_for_unknown_id():
    assert AnalysisCache().get("missing") is None


def test_expires_entries_after_ttl():
    clock = FakeClock()
    cache = AnalysisCache(ttl_seconds=60, clock=clock)
    analysis_id = cache.add(make_frames(), list(range(16)), 25.0, 1)

    clock.now = 59
    assert cache.get(analysis_id) is not None

    clock.now = 60
    assert cache.get(analysis_id) is None


def test_drops_the_oldest_entry_when_full():
    cache = AnalysisCache(max_entries=2)

    first = cache.add(make_frames(), [], 25.0, 1)
    second = cache.add(make_frames(), [], 25.0, 1)
    third = cache.add(make_frames(), [], 25.0, 1)

    assert cache.get(first) is None
    assert cache.get(second) is not None
    assert cache.get(third) is not None
