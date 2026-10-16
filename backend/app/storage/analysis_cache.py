import threading
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass

import numpy as np


@dataclass
class CachedAnalysis:
    # Sampled frames as RGB images: (K_FRAMES, IMG_SIZE, IMG_SIZE, 3), uint8
    frames: np.ndarray
    frame_numbers: list[int]
    fps: float
    # Class the model predicted (0 = real, 1 = fake), explained by Grad-CAM
    predicted_class: int
    created_at: float
    # Grad-CAM maps for all frames: (K_FRAMES, IMG_SIZE, IMG_SIZE),
    # computed on the first request
    heatmaps: np.ndarray | None = None


class AnalysisCache:
    """Keeps recent analyses in memory so their frames can be fetched later.

    Old entries expire after ttl_seconds, and the oldest entry is dropped
    once max_entries is reached.
    """

    def __init__(self, max_entries=20, ttl_seconds=30 * 60, clock=time.monotonic):
        self._entries = OrderedDict()
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        # GET endpoints run in FastAPI's thread pool
        self._lock = threading.Lock()

    def add(self, frames, frame_numbers, fps, predicted_class):
        analysis_id = str(uuid.uuid4())

        with self._lock:
            self._remove_expired()

            self._entries[analysis_id] = CachedAnalysis(
                frames=frames,
                frame_numbers=frame_numbers,
                fps=fps,
                predicted_class=predicted_class,
                created_at=self._clock()
            )

            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)

        return analysis_id

    def get(self, analysis_id):
        with self._lock:
            self._remove_expired()
            return self._entries.get(analysis_id)

    def _remove_expired(self):
        now = self._clock()

        # Entries are kept in insertion order, so the oldest come first
        while self._entries:
            oldest = next(iter(self._entries.values()))

            if now - oldest.created_at < self._ttl_seconds:
                break

            self._entries.popitem(last=False)
