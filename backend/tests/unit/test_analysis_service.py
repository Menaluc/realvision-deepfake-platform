import io

import pytest

from app.config import Settings
from app.errors import UnreadableVideo, UnsupportedMediaType, VideoTooLarge
from app.ml.preprocess import IMG_SIZE, K_FRAMES
from app.services.analysis import analyze_upload
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
