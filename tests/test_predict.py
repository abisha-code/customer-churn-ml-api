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


def test_predict_valid_input_returns_200_and_sensible_prediction(client):
    response = client.post("/api/v1/predict", json=VALID_CUSTOMER)
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] in ("Churn", "No Churn")
    assert 0.0 <= data["confidence"] <= 1.0
    assert "request_id" in data
    assert "model_version" in data


def test_predict_missing_field_returns_422(client):
    bad_customer = VALID_CUSTOMER.copy()
    del bad_customer["Total Charges"]  
    response = client.post("/api/v1/predict", json=bad_customer)
    assert response.status_code == 422


def test_predict_invalid_type_returns_422(client):
    bad_customer = VALID_CUSTOMER.copy()
    bad_customer["Monthly Charges"] = "not_a_number"   
    response = client.post("/api/v1/predict", json=bad_customer)
    assert response.status_code == 422


def test_predict_negative_tenure_returns_422(client):
    bad_customer = VALID_CUSTOMER.copy()
    bad_customer["Tenure Months"] = -5   
    response = client.post("/api/v1/predict", json=bad_customer)
    assert response.status_code == 422
