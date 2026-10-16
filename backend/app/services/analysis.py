"""Runs one upload through the pipeline: checks, preprocessing, prediction, cache."""

from typing import BinaryIO

from app.config import Settings
from app.ml.predictor import Prediction, Predictor
from app.ml.preprocess import preprocess_video
from app.services.upload import saved_upload
from app.services.validation import check_declared_type, check_readable_video
from app.storage.analysis_cache import AnalysisCache


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

    prediction = predictor.predict(sampled.tensor)

    # Keep the sampled frames so the client can fetch them afterwards
    analysis_id = cache.add(
        sampled.frames,
        sampled.frame_numbers,
        sampled.fps,
        prediction.predicted_class,
    )

    return analysis_id, prediction
