import io
import threading
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
import pytest
import torch

from app.config import Settings
from app.errors import (
    AnalysisNotFound,
    FrameNotFound,
    UnreadableVideo,
    UnsupportedMediaType,
    VideoTooLarge,
)
from app.ml.preprocess import IMG_SIZE, K_FRAMES
from app.services.analysis import (
    analyze_upload,
    attention_png,
    frame_jpeg,
    list_frames,
)
from app.storage.analysis_cache import AnalysisCache
from tests.fakes import FakePredictor


@pytest.fixture
def upload_dir(tmp_path):
    path = tmp_path / "uploads"
    path.mkdir()
    return path


@pytest.fixture
def settings(upload_dir):
    return Settings(temp_dir=upload_dir)


@pytest.fixture
def predictor():
    return FakePredictor(label="fake", confidence=0.8)


@pytest.fixture
def cache():
    return AnalysisCache()


def analyze(path, settings, predictor, cache, content_type="video/mp4"):
    return analyze_upload(
        io.BytesIO(path.read_bytes()),
        path.name,
        content_type,
        settings,
        predictor,
        cache,
    )


def test_runs_the_real_preprocessing_and_caches_the_frames(
    video_file, settings, predictor, cache, upload_dir
):
    analysis_id, prediction = analyze(video_file, settings, predictor, cache)

    # The model sees exactly what preprocess_video produces
    (tensor,) = predictor.received
    assert tensor.shape == (K_FRAMES, 3, IMG_SIZE, IMG_SIZE)

    assert prediction.label == "fake"

    cached = cache.get(analysis_id)
    assert cached.frames.shape == (K_FRAMES, IMG_SIZE, IMG_SIZE, 3)
    assert cached.predicted_class == prediction.predicted_class
    assert cached.heatmaps is None

    assert list(upload_dir.iterdir()) == []


def test_checks_the_type_before_saving(video_file, settings, predictor, cache):
    with pytest.raises(UnsupportedMediaType):
        analyze(video_file, settings, predictor, cache, content_type="image/png")


def test_checks_the_size_while_saving(video_file, predictor, cache, upload_dir):
    settings = Settings(temp_dir=upload_dir, max_upload_bytes=10)

    with pytest.raises(VideoTooLarge):
        analyze(video_file, settings, predictor, cache)


@pytest.mark.parametrize("fixture", ["junk_file", "empty_video_file"])
def test_unreadable_video_never_reaches_the_model(
    request, fixture, settings, predictor, cache, upload_dir
):
    with pytest.raises(UnreadableVideo):
        analyze(request.getfixturevalue(fixture), settings, predictor, cache)

    assert predictor.received == []
    assert list(upload_dir.iterdir()) == []


# --- frames and attention ---


@pytest.fixture
def analysis_id(video_file, settings, predictor, cache):
    analysis_id, _ = analyze(video_file, settings, predictor, cache)
    return analysis_id


def test_lists_every_sampled_frame_with_its_time(cache, analysis_id):
    frames = list_frames(cache, analysis_id)
    cached = cache.get(analysis_id)

    assert [frame.index for frame in frames] == list(range(K_FRAMES))
    assert [frame.frame_number for frame in frames] == cached.frame_numbers
    for frame in frames:
        assert frame.timestamp == pytest.approx(frame.frame_number / cached.fps)


def test_timestamp_is_unknown_without_a_frame_rate(cache):
    frames = np.zeros((2, IMG_SIZE, IMG_SIZE, 3), np.uint8)
    analysis_id = cache.add(frames, [0, 5], fps=0.0, predicted_class=1)

    assert [frame.timestamp for frame in list_frames(cache, analysis_id)] == [
        None,
        None,
    ]


def test_frame_jpeg_shows_the_cached_frame(cache, analysis_id):
    jpeg = frame_jpeg(cache, analysis_id, 3)

    decoded = cv2.cvtColor(
        cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR),
        cv2.COLOR_BGR2RGB,
    )
    original = cache.get(analysis_id).frames[3]

    assert decoded.shape == original.shape
    # JPEG is lossy, so close rather than equal
    assert np.abs(decoded.astype(int) - original.astype(int)).mean() < 3


def test_attention_explains_the_prediction_on_the_same_tensor(
    cache, predictor, analysis_id
):
    png = attention_png(cache, predictor, analysis_id, 0)

    assert png.startswith(b"\x89PNG")

    ((explained_tensor, target_class),) = predictor.explained
    (predicted_tensor,) = predictor.received
    # Grad-CAM sees exactly what the model saw, and explains its decision
    assert torch.equal(explained_tensor, predicted_tensor)
    assert target_class == cache.get(analysis_id).predicted_class


def test_attention_is_computed_once_for_concurrent_requests(
    video_file, settings, cache
):
    predictor = FakePredictor(explain_seconds=0.2)
    analysis_id, _ = analyze(video_file, settings, predictor, cache)
    start = threading.Barrier(K_FRAMES)

    def request(index):
        start.wait()
        return attention_png(cache, predictor, analysis_id, index)

    with ThreadPoolExecutor(K_FRAMES) as pool:
        pngs = list(pool.map(request, range(K_FRAMES)))

    assert len(predictor.explained) == 1
    assert all(png.startswith(b"\x89PNG") for png in pngs)


def test_unknown_analysis_is_not_found(cache, predictor):
    unknown = "00000000-0000-4000-8000-000000000000"

    with pytest.raises(AnalysisNotFound):
        list_frames(cache, unknown)
    with pytest.raises(AnalysisNotFound):
        frame_jpeg(cache, unknown, 0)
    with pytest.raises(AnalysisNotFound):
        attention_png(cache, predictor, unknown, 0)


@pytest.mark.parametrize("index", [K_FRAMES, -1])
def test_index_out_of_range_is_not_found(cache, predictor, analysis_id, index):
    with pytest.raises(FrameNotFound):
        frame_jpeg(cache, analysis_id, index)
    with pytest.raises(FrameNotFound):
        attention_png(cache, predictor, analysis_id, index)

    # Rejected before any Grad-CAM work
    assert predictor.explained == []
