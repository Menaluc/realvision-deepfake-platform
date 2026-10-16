"""Analyses: running an upload through the pipeline, then serving its frames
and Grad-CAM heatmaps from the cache."""

import threading
from dataclasses import dataclass
from typing import BinaryIO

import cv2

from app.config import Settings
from app.errors import AnalysisNotFound, FrameNotFound
from app.ml.gradcam import heatmap_to_png
from app.ml.predictor import Prediction, Predictor
from app.ml.preprocess import frames_to_tensor, preprocess_video
from app.services.upload import saved_upload
from app.services.validation import check_declared_type, check_readable_video
from app.storage.analysis_cache import AnalysisCache, CachedAnalysis

JPEG_QUALITY = 90

# Guards the first Grad-CAM run of each analysis, so it happens once even when
# the client asks for all frames at the same time. It costs no throughput:
# the predictor's own lock already runs one model call at a time.
_heatmap_lock = threading.Lock()


@dataclass(frozen=True)
class FrameDescription:
    index: int
    frame_number: int
    # Seconds from the start of the video; None if the frame rate is unknown
    timestamp: float | None


def analyze_upload(
    source: BinaryIO,
    filename: str | None,
    content_type: str | None,
    settings: Settings,
    predictor: Predictor,
    cache: AnalysisCache,
) -> tuple[str, Prediction]:
    """Returns the new analysis id and the prediction.

    Raises UnsupportedMediaType, VideoTooLarge or UnreadableVideo, in that
    order. The temp file is gone when this returns or raises.
    """
    check_declared_type(content_type)

    with saved_upload(
        source, filename, settings.max_upload_bytes, settings.temp_dir
    ) as path:
        check_readable_video(path)
        sampled = preprocess_video(str(path))

    # Outside the with-block: the frames are in memory now, so the temp file
    # is deleted before the slowest step instead of after it
    prediction = predictor.predict(sampled.tensor)

    # Keep the sampled frames so the client can fetch them afterwards
    analysis_id = cache.add(
        sampled.frames,
        sampled.frame_numbers,
        sampled.fps,
        prediction.predicted_class,
    )

    return analysis_id, prediction


def get_analysis(cache: AnalysisCache, analysis_id: str) -> CachedAnalysis:
    analysis = cache.get(analysis_id)

    if analysis is None:
        raise AnalysisNotFound()

    return analysis


def get_frame_index(analysis: CachedAnalysis, index: int) -> int:
    if not 0 <= index < len(analysis.frames):
        raise FrameNotFound()

    return index


def list_frames(cache: AnalysisCache, analysis_id: str) -> list[FrameDescription]:
    analysis = get_analysis(cache, analysis_id)

    return [
        FrameDescription(
            index=index,
            frame_number=frame_number,
            timestamp=frame_number / analysis.fps if analysis.fps > 0 else None,
        )
        for index, frame_number in enumerate(analysis.frame_numbers)
    ]


def frame_jpeg(cache: AnalysisCache, analysis_id: str, index: int) -> bytes:
    analysis = get_analysis(cache, analysis_id)
    index = get_frame_index(analysis, index)

    # Frames are RGB, OpenCV encodes BGR
    frame = cv2.cvtColor(analysis.frames[index], cv2.COLOR_RGB2BGR)
    ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])

    if not ok:
        raise RuntimeError("Failed to encode frame")

    return jpeg.tobytes()


def attention_png(
    cache: AnalysisCache, predictor: Predictor, analysis_id: str, index: int
) -> bytes:
    analysis = get_analysis(cache, analysis_id)
    index = get_frame_index(analysis, index)

    # Double-checked: the second check sees maps that another request
    # computed while this one waited for the lock
    if analysis.heatmaps is None:
        with _heatmap_lock:
            if analysis.heatmaps is None:
                # The cached frames give the same tensor the prediction used,
                # and Grad-CAM explains the class that was predicted.
                # Stored on the cached entry itself: heatmaps is the lazy
                # field AnalysisCache leaves for this.
                analysis.heatmaps = predictor.explain(
                    frames_to_tensor(analysis.frames), analysis.predicted_class
                )

    return heatmap_to_png(analysis.heatmaps[index])
