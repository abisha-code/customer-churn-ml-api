def test_model_info_returns_expected_metadata_keys(client):
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200

    data = response.json()
    expected_keys = {"model_type", "model_version", "trained_on", "features"}
    assert expected_keys.issubset(data.keys())
    assert isinstance(data["features"], list)
    assert len(data["features"]) > 0
