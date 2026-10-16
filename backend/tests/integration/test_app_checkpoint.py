from pathlib import Path

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
