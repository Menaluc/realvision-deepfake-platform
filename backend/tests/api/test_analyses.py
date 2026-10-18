import uuid

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services.upload import CONTENT_LENGTH_MARGIN
from tests.fakes import FakePredictor

URL = "/api/analyses"


def upload(client, path, content_type="video/mp4", field="video", **kwargs):
    files = {field: (path.name, path.read_bytes(), content_type)}
    return client.post(URL, files=files, **kwargs)


def assert_error(response, status_code, code):
    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code


@pytest.fixture(autouse=True)
def no_temp_files_left(upload_dir):
    # Every test in this module, success or error, must leave no upload behind
    yield
    assert list(upload_dir.iterdir()) == []


# --- success ---


def test_creates_an_analysis(client, ready_app, video_file):
    response = upload(client, video_file)

    assert response.status_code == 201
    assert "location" not in response.headers

    body = response.json()
    assert body == {
        "id": body["id"],
        "prediction": "fake",
        "confidence": 0.9,
        "probabilities": {"real": pytest.approx(0.1), "fake": 0.9},
    }
    uuid.UUID(body["id"])
    assert ready_app.state.cache.get(body["id"]) is not None


def test_reports_a_real_prediction(upload_dir, video_file):
    settings = Settings(temp_dir=upload_dir)
    app = create_app(settings, predictor=FakePredictor(label="real", confidence=0.7))

    body = upload(TestClient(app), video_file).json()

    assert body["prediction"] == "real"
    assert body["confidence"] == 0.7


# --- errors, in the order they are checked ---


def test_model_unavailable_comes_first(degraded_client, video_file):
    assert_error(upload(degraded_client, video_file), 503, "MODEL_UNAVAILABLE")


def test_model_unavailable_wins_over_a_large_content_length(degraded_client):
    response = degraded_client.post(
        URL, content=b"x", headers={"content-length": str(10**9)}
    )

    assert_error(response, 503, "MODEL_UNAVAILABLE")


def test_rejects_a_large_content_length_before_reading_the_body(client, fake_predictor):
    limit = Settings().max_upload_bytes
    response = client.post(
        URL,
        content=b"x",
        headers={"content-length": str(limit + CONTENT_LENGTH_MARGIN + 1)},
    )

    assert_error(response, 413, "VIDEO_TOO_LARGE")
    assert fake_predictor.received == []


def test_missing_video_field_is_a_bad_request(client, video_file):
    assert_error(upload(client, video_file, field="file"), 400, "INVALID_REQUEST")


def test_non_multipart_body_is_a_bad_request(client):
    assert_error(client.post(URL, json={"video": "x"}), 400, "INVALID_REQUEST")


def test_non_video_type_is_unsupported(client, video_file):
    response = upload(client, video_file, content_type="image/png")

    assert_error(response, 415, "UNSUPPORTED_MEDIA_TYPE")


def test_file_over_the_limit_is_rejected_while_copying(upload_dir, video_file):
    # The body is small enough to pass the Content-Length precheck
    settings = Settings(temp_dir=upload_dir, max_upload_bytes=100)
    client = TestClient(create_app(settings, predictor=FakePredictor()))

    assert_error(upload(client, video_file), 413, "VIDEO_TOO_LARGE")


@pytest.mark.parametrize(
    "fixture", ["junk_file", "empty_video_file", "truncated_video_file"]
)
def test_unreadable_video(request, client, fixture, fake_predictor):
    response = upload(client, request.getfixturevalue(fixture))

    assert_error(response, 422, "UNREADABLE_VIDEO")
    assert fake_predictor.received == []


def test_model_failure_is_a_generic_server_error(upload_dir, video_file):
    class BrokenPredictor(FakePredictor):
        def predict(self, video_tensor):
            raise RuntimeError("secret internal detail")

    settings = Settings(temp_dir=upload_dir)
    app = create_app(settings, predictor=BrokenPredictor())
    client = TestClient(app, raise_server_exceptions=False)

    response = upload(client, video_file)

    assert_error(response, 500, "INTERNAL_ERROR")
    assert "secret" not in response.text
