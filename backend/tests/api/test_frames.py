import cv2
import numpy as np
import pytest

from app.ml.preprocess import IMG_SIZE, K_FRAMES

UNKNOWN_ID = "00000000-0000-4000-8000-000000000000"


def assert_error(response, status_code, code):
    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code


@pytest.fixture
def analysis_id(client, video_file):
    files = {"video": (video_file.name, video_file.read_bytes(), "video/mp4")}
    return client.post("/api/analyses", files=files).json()["id"]


def decode(response, flags):
    return cv2.imdecode(np.frombuffer(response.content, np.uint8), flags)


# --- frames list ---


def test_lists_the_sampled_frames(client, analysis_id):
    response = client.get(f"/api/analyses/{analysis_id}/frames")

    assert response.status_code == 200
    frames = response.json()["frames"]
    assert [frame["index"] for frame in frames] == list(range(K_FRAMES))
    assert set(frames[0]) == {"index", "frameNumber", "timestamp"}


# --- frame image ---


def test_serves_a_frame_as_jpeg(client, analysis_id):
    response = client.get(f"/api/analyses/{analysis_id}/frames/0")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert decode(response, cv2.IMREAD_COLOR).shape == (IMG_SIZE, IMG_SIZE, 3)


# --- attention ---


def test_serves_attention_as_a_transparent_png(client, analysis_id):
    response = client.get(f"/api/analyses/{analysis_id}/frames/0/attention")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    # Four channels: the heat sets the opacity
    assert decode(response, cv2.IMREAD_UNCHANGED).shape == (IMG_SIZE, IMG_SIZE, 4)


def test_attention_is_computed_once_per_analysis(client, analysis_id, fake_predictor):
    for index in (0, 5, 0):
        response = client.get(f"/api/analyses/{analysis_id}/frames/{index}/attention")
        assert response.status_code == 200

    assert len(fake_predictor.explained) == 1


def test_attention_needs_the_model(degraded_client):
    response = degraded_client.get(f"/api/analyses/{UNKNOWN_ID}/frames/0/attention")

    assert_error(response, 503, "MODEL_UNAVAILABLE")


def test_model_unavailable_comes_before_request_errors(degraded_client):
    # Pins FastAPI's order: dependencies run before path validation
    response = degraded_client.get("/api/analyses/not-a-uuid/frames/-1/attention")

    assert_error(response, 503, "MODEL_UNAVAILABLE")


# --- errors on every frame endpoint ---

FRAME_PATHS = ["/frames", "/frames/0", "/frames/0/attention"]


@pytest.mark.parametrize("suffix", FRAME_PATHS)
def test_unknown_analysis_is_not_found(client, suffix):
    response = client.get(f"/api/analyses/{UNKNOWN_ID}{suffix}")

    assert_error(response, 404, "ANALYSIS_NOT_FOUND")


@pytest.mark.parametrize("suffix", FRAME_PATHS)
def test_malformed_id_is_a_bad_request(client, suffix):
    assert_error(
        client.get(f"/api/analyses/not-a-uuid{suffix}"), 400, "INVALID_REQUEST"
    )


@pytest.mark.parametrize("suffix", ["", "/attention"])
@pytest.mark.parametrize("index", ["-1", "abc"])
def test_invalid_index_is_a_bad_request(client, analysis_id, suffix, index):
    response = client.get(f"/api/analyses/{analysis_id}/frames/{index}{suffix}")

    assert_error(response, 400, "INVALID_REQUEST")


@pytest.mark.parametrize("suffix", ["", "/attention"])
def test_index_past_the_last_frame_is_not_found(client, analysis_id, suffix):
    response = client.get(f"/api/analyses/{analysis_id}/frames/{K_FRAMES}{suffix}")

    assert_error(response, 404, "FRAME_NOT_FOUND")


@pytest.mark.parametrize("suffix", ["/frames", "/frames/0"])
def test_frames_are_not_found_in_degraded_mode(degraded_client, suffix):
    # They don't need the model, but nothing can be in the cache
    response = degraded_client.get(f"/api/analyses/{UNKNOWN_ID}{suffix}")

    assert_error(response, 404, "ANALYSIS_NOT_FOUND")
