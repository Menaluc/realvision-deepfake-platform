import logging

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from tests.fakes import FakePredictor


@pytest.fixture
def frontend_dist(tmp_path):
    # A minimal stand-in for frontend/dist after npm run build
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>RealVision</title>")
    (dist / "assets" / "app.js").write_text("console.log('app')")
    return dist


def make_client(tmp_path, frontend_dist, predictor=None):
    settings = Settings(
        checkpoint_path=tmp_path / "missing.pt", frontend_dist=frontend_dist
    )
    return TestClient(create_app(settings, predictor=predictor))


@pytest.fixture
def client(tmp_path, frontend_dist):
    return make_client(tmp_path, frontend_dist, FakePredictor())


def test_serves_the_page_at_the_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "RealVision" in response.text


def test_serves_the_built_assets(client):
    response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert "console.log" in response.text


def test_api_still_wins_over_the_static_files(client):
    assert client.get("/api/health").json() == {"status": "ok", "modelLoaded": True}
    assert client.get("/api/model").json()["backbone"] == "fake_backbone"


@pytest.mark.parametrize("path", ["/api/nope", "/nope"])
def test_unknown_paths_are_not_found_in_the_error_format(client, path):
    response = client.get(path)

    # No client-side routing, so no index.html fallback
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_degraded_app_still_serves_the_page(tmp_path, frontend_dist):
    client = make_client(tmp_path, frontend_dist)

    assert client.get("/").status_code == 200
    assert client.get("/api/health").status_code == 503


def test_without_a_build_only_the_api_is_served(tmp_path, caplog):
    with caplog.at_level(logging.INFO):
        client = make_client(tmp_path, tmp_path / "missing-dist", FakePredictor())

    assert client.get("/api/health").status_code == 200
    assert client.get("/").json()["error"]["code"] == "NOT_FOUND"
    assert "serving the API only" in caplog.text
