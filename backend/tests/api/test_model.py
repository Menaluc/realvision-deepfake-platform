def test_model_info_comes_from_the_predictor(client):
    response = client.get("/api/model")

    assert response.status_code == 200
    assert response.json() == {
        "backbone": "fake_backbone",
        "sampledFrames": 16,
        "inputSize": 224,
        "featureSize": 1280,
        "embeddingSize": 256,
        "classes": ["real", "fake"],
    }


def test_model_info_is_unavailable_without_the_model(degraded_client):
    response = degraded_client.get("/api/model")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MODEL_UNAVAILABLE"
