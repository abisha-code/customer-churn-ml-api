import httpx

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "supersecretkey123"  # match your real .env value

VALID_CUSTOMER = {
    "Tenure Months": 12, "Monthly Charges": 75.50, "Total Charges": 906.00,
    "Gender": "Female", "Senior Citizen": "No", "Partner": "Yes",
    "Dependents": "No", "Phone Service": "Yes", "Multiple Lines": "No",
    "Internet Service": "Fiber optic", "Online Security": "No",
    "Online Backup": "No", "Device Protection": "No", "Tech Support": "No",
    "Streaming TV": "Yes", "Streaming Movies": "Yes",
    "Contract": "Month-to-month", "Paperless Billing": "Yes",
    "Payment Method": "Electronic check",
}


def test_health_reachable_over_real_http():
    r = httpx.get(f"{BASE_URL}/api/v1/health")
    assert r.status_code == 200
    assert r.json()["model_loaded"] is True


def test_predict_reachable_over_real_http():
    r = httpx.post(
        f"{BASE_URL}/api/v1/predict",
        json=VALID_CUSTOMER,
        headers={"X-API-Key": API_KEY},
    )
    assert r.status_code == 200
    assert "prediction" in r.json()


def test_predict_batch_reachable_over_real_http():
    r = httpx.post(
        f"{BASE_URL}/api/v1/predict-batch",
        json={"customers": [VALID_CUSTOMER, VALID_CUSTOMER]},
        headers={"X-API-Key": API_KEY},
    )
    assert r.status_code == 200
    assert r.json()["batch_size"] == 2


def test_metrics_reachable_and_valid_prometheus_format():
    r = httpx.get(f"{BASE_URL}/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
