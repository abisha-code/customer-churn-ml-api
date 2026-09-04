VALID_CUSTOMER = {
    "Tenure Months": 12,
    "Monthly Charges": 75.50,
    "Total Charges": 906.00,
    "Gender": "Female",
    "Senior Citizen": "No",
    "Partner": "Yes",
    "Dependents": "No",
    "Phone Service": "Yes",
    "Multiple Lines": "No",
    "Internet Service": "Fiber optic",
    "Online Security": "No",
    "Online Backup": "No",
    "Device Protection": "No",
    "Tech Support": "No",
    "Streaming TV": "Yes",
    "Streaming Movies": "Yes",
    "Contract": "Month-to-month",
    "Paperless Billing": "Yes",
    "Payment Method": "Electronic check",
}


def test_predict_batch_valid_small_batch_returns_200(client):
    payload = {"customers": [VALID_CUSTOMER, VALID_CUSTOMER]}
    response = client.post("/api/v1/predict-batch", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["batch_size"] == 2
    assert len(data["predictions"]) == 2


def test_predict_batch_oversized_batch_is_rejected(client):
    # settings.MAX_BATCH_SIZE is 100 by default -- 150 exceeds it
    payload = {"customers": [VALID_CUSTOMER] * 150}
    response = client.post("/api/v1/predict-batch", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum allowed" in response.json()["detail"]


def test_predict_batch_empty_list_returns_422(client):
    response = client.post("/api/v1/predict-batch", json={"customers": []})
    assert response.status_code == 422
