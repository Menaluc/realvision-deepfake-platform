import logging

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_missing_checkpoint_starts_degraded_and_logs_why(tmp_path, caplog):
    checkpoint = tmp_path / "missing.pt"

    with caplog.at_level(logging.WARNING):
        app = create_app(Settings(checkpoint_path=checkpoint))

    assert app.state.predictor is None
    assert "degraded" in caplog.text
    assert "missing.pt" in caplog.text


def test_corrupt_checkpoint_starts_degraded(tmp_path, caplog):
    checkpoint = tmp_path / "corrupt.pt"
    checkpoint.write_bytes(b"not a checkpoint")

    with caplog.at_level(logging.WARNING):
        app = create_app(Settings(checkpoint_path=checkpoint))

    assert app.state.predictor is None
    assert "corrupt.pt" in caplog.text
    # The app still serves requests
    assert TestClient(app).get("/api/health").status_code == 503


def test_settings_are_read_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("REALVISION_CHECKPOINT_PATH", str(tmp_path / "model.pt"))
    monkeypatch.setenv("REALVISION_DEVICE", "cuda")
    monkeypatch.setenv("REALVISION_CACHE_MAX_ENTRIES", "5")

    settings = Settings.from_env()

    assert settings.checkpoint_path == tmp_path / "model.pt"
    assert settings.device == "cuda"
    assert settings.cache_max_entries == 5
    # Unset variables keep their defaults
    assert settings.cache_ttl_seconds == Settings().cache_ttl_seconds


def test_importing_main_does_not_load_the_model():
    import app.main

    # Only a factory: no app (and no model) is created at import time
    assert not hasattr(app.main, "app")
