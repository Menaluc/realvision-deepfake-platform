import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.ml.predictor import CLASSES, ModelInfo


class FakePredictor:
    """Stands in for Predictor, so API tests don't need the checkpoint."""

    def info(self) -> ModelInfo:
        return ModelInfo(
            backbone="fake_backbone",
            sampled_frames=16,
            input_size=224,
            feature_size=1280,
            embedding_size=256,
            classes=CLASSES,
        )


@pytest.fixture
def missing_checkpoint_settings(tmp_path):
    return Settings(checkpoint_path=tmp_path / "missing.pt")


@pytest.fixture
def ready_app(missing_checkpoint_settings):
    # The fake predictor wins: the missing checkpoint is never read
    return create_app(missing_checkpoint_settings, predictor=FakePredictor())


@pytest.fixture
def degraded_app(missing_checkpoint_settings):
    return create_app(missing_checkpoint_settings)


@pytest.fixture
def client(ready_app):
    return TestClient(ready_app)


@pytest.fixture
def degraded_client(degraded_app):
    return TestClient(degraded_app)
