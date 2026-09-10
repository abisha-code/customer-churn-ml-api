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


def test_predict_without_api_key_returns_401(client):
    response = client.post(
        "/api/v1/predict",
        json=VALID_CUSTOMER,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_predict_with_invalid_api_key_returns_401(client):
    response = client.post(
        "/api/v1/predict",
        json=VALID_CUSTOMER,
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_predict_with_valid_api_key_returns_200(client):
    response = client.post(
        "/api/v1/predict",
        json=VALID_CUSTOMER,
        headers={"X-API-Key": "supersecretkey123"},
    )

    assert response.status_code == 200


def test_predict_rejects_unexpected_extra_field(client):
    bad_customer = dict(VALID_CUSTOMER)
    bad_customer["unexpected_field"] = "hacker_injected"

    response = client.post(
        "/api/v1/predict",
        json=bad_customer,
        headers={"X-API-Key": "supersecretkey123"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"
