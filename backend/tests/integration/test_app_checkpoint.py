from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

# The real checkpoint is copied in by hand and never committed
CHECKPOINT = Path(__file__).resolve().parents[2] / "models" / "baseline_best.pt"

pytestmark = pytest.mark.skipif(
    not CHECKPOINT.is_file(), reason=f"checkpoint not found at {CHECKPOINT}"
)


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app(Settings(checkpoint_path=CHECKPOINT)))


def test_app_starts_ready_with_the_real_checkpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "modelLoaded": True}


def test_analyzes_a_video_with_the_real_model(client, video_file):
    files = {"video": (video_file.name, video_file.read_bytes(), "video/mp4")}
    response = client.post("/api/analyses", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["prediction"] in ("real", "fake")
    assert body["confidence"] == body["probabilities"][body["prediction"]]
    assert sum(body["probabilities"].values()) == pytest.approx(1.0)


def test_serves_real_grad_cam_for_an_analysis(client, video_file):
    files = {"video": (video_file.name, video_file.read_bytes(), "video/mp4")}
    analysis_id = client.post("/api/analyses", files=files).json()["id"]

    response = client.get(f"/api/analyses/{analysis_id}/frames/0/attention")

    assert response.status_code == 200
    png = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_UNCHANGED)
    assert png.shape == (224, 224, 4)


def test_model_info_is_read_from_the_real_model(client):
    response = client.get("/api/model")

    assert response.status_code == 200
    assert response.json() == {
        "backbone": "tf_efficientnet_b0",
        "sampledFrames": 16,
        "inputSize": 224,
        "featureSize": 1280,
        "embeddingSize": 256,
        "classes": ["real", "fake"],
    }
