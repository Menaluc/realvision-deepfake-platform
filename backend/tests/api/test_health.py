def test_health_is_ok_when_the_model_is_loaded(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "modelLoaded": True}


def test_health_is_degraded_without_the_model(degraded_client):
    response = degraded_client.get("/api/health")

    # A status endpoint: the 503 keeps the health body, not the error format
    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "modelLoaded": False}
