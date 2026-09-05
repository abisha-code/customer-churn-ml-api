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


def test_v1_and_v2_predict_return_different_but_individually_correct_shapes(client):
    v1_response = client.post("/api/v1/predict", json=VALID_CUSTOMER)
    v2_response = client.post("/api/v2/predict", json=VALID_CUSTOMER)

    assert v1_response.status_code == 200
    assert v2_response.status_code == 200

    v1_data = v1_response.json()
    v2_data = v2_response.json()

    # v1's contract: has "confidence", does NOT have "probabilities"
    assert "confidence" in v1_data
    assert "probabilities" not in v1_data
    assert v1_data["model_version"] == "1.0.0"

    # v2's contract: has "probabilities", does NOT have "confidence"
    assert "probabilities" in v2_data
    assert "confidence" not in v2_data
    assert v2_data["model_version"] == "2.0.0"

    # Both agree on the actual prediction itself (same model, same input)
    assert v1_data["prediction"] == v2_data["prediction"]

    # The shapes are provably different dictionaries
    assert set(v1_data.keys()) != set(v2_data.keys())
