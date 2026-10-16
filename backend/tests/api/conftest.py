import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from tests.fakes import FakePredictor


@pytest.fixture
def upload_dir(tmp_path):
    # Uploads go here, so tests can check that no temp file is left behind
    path = tmp_path / "uploads"
    path.mkdir()
    return path


@pytest.fixture
def missing_checkpoint_settings(tmp_path, upload_dir):
    return Settings(
        checkpoint_path=tmp_path / "missing.pt",
        temp_dir=upload_dir,
        # API tests don't depend on whether a local frontend build exists
        frontend_dist=tmp_path / "no-frontend-build",
    )


@pytest.fixture
def fake_predictor():
    return FakePredictor()


@pytest.fixture
def ready_app(missing_checkpoint_settings, fake_predictor):
    # The fake predictor wins: the missing checkpoint is never read
    return create_app(missing_checkpoint_settings, predictor=fake_predictor)


@pytest.fixture
def degraded_app(missing_checkpoint_settings):
    return create_app(missing_checkpoint_settings)


@pytest.fixture
def client(ready_app):
    return TestClient(ready_app)


@pytest.fixture
def degraded_client(degraded_app):
    return TestClient(degraded_app)
