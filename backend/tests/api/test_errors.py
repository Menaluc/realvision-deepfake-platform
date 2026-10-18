import logging

import pytest
from fastapi.testclient import TestClient


def assert_error(response, status_code, code):
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]


@pytest.fixture
def app_with_test_routes(ready_app):
    # Routes that exist only in these tests, to reach handlers that the
    # stage-4 endpoints can't trigger yet
    @ready_app.get("/api/test/items/{index}")
    def typed_item(index: int):
        return {"index": index}

    @ready_app.get("/api/test/crash")
    def crash():
        raise RuntimeError("secret internal detail")

    return ready_app


def test_unknown_api_route_is_not_found(client):
    assert_error(client.get("/api/does-not-exist"), 404, "NOT_FOUND")


def test_wrong_method_is_not_allowed(client):
    response = client.post("/api/health")

    assert_error(response, 405, "METHOD_NOT_ALLOWED")
    assert response.headers["allow"] == "GET"


def test_invalid_path_parameter_is_a_bad_request(app_with_test_routes):
    response = TestClient(app_with_test_routes).get("/api/test/items/abc")

    # 400, not FastAPI's default 422
    assert_error(response, 400, "INVALID_REQUEST")


def test_unexpected_error_is_generic_and_logged(app_with_test_routes, caplog):
    # Otherwise TestClient re-raises the error instead of returning the 500
    client = TestClient(app_with_test_routes, raise_server_exceptions=False)

    with caplog.at_level(logging.ERROR):
        response = client.get("/api/test/crash")

    assert_error(response, 500, "INTERNAL_ERROR")
    assert "secret internal detail" not in response.text
    assert "secret internal detail" in caplog.text
