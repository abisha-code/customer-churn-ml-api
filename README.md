# ML Model Deployment as a Monitored REST API

## Project Overview

This project builds a **Customer Churn Prediction API** using the Telco Customer Churn dataset and a Logistic Regression model. The trained model is served through **FastAPI**, exposing versioned, authenticated, monitored prediction endpoints that determine whether a customer is likely to churn or stay.

The project was built incrementally across 20 tasks covering the full ML-API lifecycle: model training, API development, input validation, versioning, structured logging, configuration management, automated testing, Docker containerization, security hardening, Prometheus monitoring, and load testing.

\---

## Dataset — Telco Customer Churn (IBM Dataset)

|Attribute|Value|
|-|-|
|**Type**|Tabular|
|**Domain**|Telecommunications|
|**Records**|7,043 customers|
|**Raw features**|33 (19 used after cleaning)|
|**Problem type**|Binary classification|
|**Target**|`Churn Value` → `1` = churned, `0` = stayed|

**Source:** [Telco Customer Churn — IBM Dataset (Kaggle)](https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset)

### Preprocessing Pipeline

Before training, the dataset is prepared to keep only relevant and reliable information.

The preprocessing includes:

1. Remove unnecessary fields
2. Remove duplicate and leakage-related fields
3. Handle missing values
4. Select relevant features
5. Encode categorical features
6. Scale numerical features
7. Combine everything into a single ML pipeline

\---

## ML Model

**Logistic Regression** — a simple binary classification model used to predict whether a customer is likely to churn or stay.

The trained model is stored at:

```text
ml/saved\_model/model.joblib
```

The model directory is bind-mounted into the running container, so a retrained model can be swapped in without rebuilding the Docker image (see [Docker Model Volume](#docker-model-volume)).

\---

## API Contract — Customer Churn Prediction

The Customer Churn Prediction API defines how a client application communicates with the machine learning service.

The API uses the **HTTP `POST`** method through the `/api/v1/predict` endpoint to receive 19 customer input fields in JSON format, validates the request using **Pydantic**, and passes valid data to the trained ML pipeline.

On a successful request, the API returns **HTTP `200 OK`** with the customer's churn prediction, a confidence score, a server-generated request ID, and the model version that produced it.

If the input is invalid, the API returns **HTTP `422 Unprocessable Entity`** without calling the ML model. Requests to a protected endpoint without a valid API key are rejected with **HTTP `401 Unauthorized`** before validation is even attempted.

|Key Element|Definition|
|-|-|
|**Endpoint**|`/api/v1/predict`|
|**HTTP Method**|`POST`|
|**Authentication**|Required — `X-API-Key` header|
|**Input**|19 customer features required by the trained pipeline|
|**Request Format**|JSON|
|**Input Validation**|Pydantic validates data types, required fields, allowed categories, numerical ranges, and rejects unexpected extra fields|
|**ML Processing**|Valid data is passed to the trained Scikit-Learn pipeline|
|**Prediction**|`1` → Churn, `0` → No Churn|
|**Success Status**|`200 OK`|
|**Success Response**|Prediction, confidence, model version, and request ID|
|**Auth Failure Status**|`401 Unauthorized` — missing or invalid API key|
|**Validation Failure**|`422 Unprocessable Entity` for invalid input|
|**Failure Handling**|Invalid or unauthenticated requests are rejected before reaching the ML model|
|**Request ID**|Generated per request, propagated through logs and the response|
|**Response Format**|JSON|

\---

## API Endpoints

|Endpoint|Method|Auth Required|Purpose|
|-|-|-|-|
|`/`|`GET`|No|Basic liveness check|
|`/api/v1/health`|`GET`|No|Reports API and model-loaded status|
|`/api/v1/predict`|`POST`|Yes|Predict customer churn (v1 response shape)|
|`/api/v1/predict-batch`|`POST`|Yes|Predict churn for a batch of 1–100 customers in one request|
|`/api/v1/model-info`|`GET`|No|Returns metadata about the currently loaded model|
|`/api/v2/predict`|`POST`|Yes|Predict customer churn (v2 response shape — full probability distribution instead of a single confidence value)|
|`/metrics`|`GET`|No|Prometheus-format metrics for monitoring|

Interactive API documentation is available through Swagger UI:

```text
http://localhost:8000/docs
```

`/health`, `/model-info`, and `/metrics` are deliberately left open without authentication, since these are typically accessed by monitoring tools and load balancers that aren't configured with credentials.

\---

## Authentication

Protected endpoints require an `X-API-Key` header matching the value configured in `.env`:

```bash
-H "X-API-Key: your-key-here"
```

Requests without a valid key are rejected with `401 Unauthorized` before any input validation or model inference is attempted.

CORS is explicitly restricted to known origins, configured via the `ALLOWED\_ORIGINS` environment variable — cross-origin browser requests from unlisted domains are blocked by the browser itself; direct API clients (curl, Postman, server-to-server calls) are unaffected by CORS and are protected by the API key instead.

\---

## Example Requests

### Health check

```bash
curl http://localhost:8000/api/v1/health
```

### Predict (v1)

```bash
curl -X POST http://localhost:8000/api/v1/predict \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-key-here" \\
  -d '{
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
    "Payment Method": "Electronic check"
  }'
```

### Predict (v2 — probability distribution instead of a single confidence value)

```bash
curl -X POST http://localhost:8000/api/v2/predict \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-key-here" \\
  -d '{ ... same 19 fields as v1 ... }'
```

### Batch predict

```bash
curl -X POST http://localhost:8000/api/v1/predict-batch \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-key-here" \\
  -d '{"customers": \[ { ...customer 1... }, { ...customer 2... } ]}'
```

### Model info

```bash
curl http://localhost:8000/api/v1/model-info
```

### Metrics (Prometheus format)

```bash
curl http://localhost:8000/metrics
```

\---

## Architecture Diagram

!\[Architecture diagram](Architectural\_Diagram.svg)

\---

## How to Run This Project

### Prerequisites

Make sure the following are installed:

* Docker Desktop
* Docker Compose
* A `.env` file in the project root

If `.env` does not exist, copy `.env.example` and fill in the required values, including:

```text
MODEL\_PATH=ml/saved\_model/model.joblib
LOG\_LEVEL=INFO
MAX\_BATCH\_SIZE=100
API\_TITLE=Customer Churn Prediction API
API\_KEY=your-key-here
ALLOWED\_ORIGINS=http://localhost:3000
```

`.env` is never committed to the repository — only `.env.example` (with placeholder values) is tracked in Git.

\---

### Run with Docker Compose

From the project root directory, run:

```bash
docker compose up --build
```

This command:

1. Builds the Docker image.
2. Creates the Docker Compose network.
3. Creates the API container.
4. Loads environment variables from `.env`.
5. Mounts the trained model directory.
6. Starts the FastAPI application.

The API will be available at:

* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
* **Metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

\---

### Stop the Application

To stop and remove the Docker Compose container and network:

```bash
docker compose down
```

The Docker image and host files are not removed.

\---

### Docker Model Volume

The trained model directory is mounted into the container using a bind mount:

```yaml
volumes:
  - ./ml/saved\_model:/app/ml/saved\_model
```

This allows the container to use the model stored on the host machine. The model can therefore be replaced without rebuilding the Docker image.

### Swap in a Retrained Model Without Rebuilding

Replace the existing model file:

```text
ml/saved\_model/model.joblib
```

with the newly trained model, then restart the API:

```bash
docker compose restart
```

The container will load the new model from the mounted `ml/saved\_model` directory on startup.

\---

## Configuration

All runtime settings are centralized in `app/config.py` via a Pydantic `Settings` object and loaded from environment variables — nothing is hardcoded in application code. This means behavior (batch size limits, log verbosity, API title, the API key itself) can be changed per environment (local, staging, production) without touching code.

|Variable|Purpose|
|-|-|
|`MODEL\_PATH`|Path to the trained model file|
|`LOG\_LEVEL`|Logging verbosity (e.g. `INFO`, `DEBUG`)|
|`MAX\_BATCH\_SIZE`|Maximum customers allowed in one batch request|
|`API\_TITLE`|Title shown in Swagger UI and OpenAPI schema|
|`API\_KEY`|Required value for the `X-API-Key` header|
|`ALLOWED\_ORIGINS`|Comma-separated list of origins permitted by CORS|

\---

## Logging

Every request is logged with a unique `request\_id`, generated once in middleware and threaded through validation, prediction, and error handling — allowing one request's full lifecycle to be traced through the logs even under concurrent traffic. Logs are written to both the console and a rotating file (`logs/app.log`, capped and rotated to avoid unbounded growth).

\---

## Monitoring

The API exposes a Prometheus-compatible `/metrics` endpoint, combining automatic request/latency metrics (via `prometheus-fastapi-instrumentator`) with a custom metric:

```text
churn\_predictions\_total{predicted\_class="Churn"}
churn\_predictions\_total{predicted\_class="No Churn"}
```

This tracks real prediction outcomes over time, broken down by predicted class — giving operational visibility beyond generic HTTP metrics.

\---

## Testing

The project includes both unit and integration tests.

```bash
# Unit tests (in-process, no running server required)
pytest -v

# Integration tests (require the API running via docker compose up first)
pytest tests/test\_integration.py -v
```

Test coverage includes: health checks, valid and invalid predictions, batch size boundaries, API-key authentication (missing/invalid/valid key), unexpected-field rejection, model metadata, and a side-by-side comparison confirming `/api/v1/predict` and `/api/v2/predict` return different but individually correct response shapes.

A basic load test (`load\_test.py`) sends concurrent requests to `/api/v1/predict` to verify behavior under load; results and findings are documented in `TESTING.md`.

\---

## Docker Configuration

The project uses:

* **Python 3.11 (slim base image)**
* **Docker**
* **Docker Compose**
* **FastAPI**
* **Uvicorn**
* **Scikit-Learn**
* **Joblib**
* **Pydantic / Pydantic Settings**
* **prometheus-fastapi-instrumentator**

The Docker image exposes port `8000`:

```text
Host:8000 → Container:8000
```

The application listens on `0.0.0.0:8000` (not `127.0.0.1`) inside the container — required so traffic forwarded in from the host via Docker's port mapping is actually reachable; binding to `127.0.0.1` would make the server unreachable from outside the container even with correct port mapping.

\---

## Project Structure

```text
customer-churn-ml-api/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── security.py
│   ├── metrics.py
│   ├── logging\_config.py
│   ├── routers/
│   │   ├── v1.py
│   │   └── v2.py
│   ├── models/
│   │   └── schemas.py
│   └── services/
│       └── prediction\_service.py
│
├── ml/
│   └── saved\_model/
│       └── model.joblib
│
├── data/
│   └── ...
│
├── tests/
│   ├── conftest.py
│   ├── test\_health.py
│   ├── test\_predict.py
│   ├── test\_predict\_batch.py
│   ├── test\_model\_info.py
│   ├── test\_v2\_predict.py
│   ├── test\_security.py
│   └── test\_integration.py
│
├── logs/
│   └── ...
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── .env.example
├── requirements.txt
├── TESTING.md
├── README.md
└── Architectural\_Diagram.svg
```

\---

## Docker Compose Service

The application is configured as an `api` service in `docker-compose.yml`.

The Compose configuration provides:

* Docker image build configuration
* Port mapping
* Environment variable loading via `.env`
* Model directory bind mount
* Automatic container restart

The service can be started with:

```bash
docker compose up
```

or rebuilt and started with:

```bash
docker compose up --build
```

\---

## Live Deployment

## Live Deployment

**URL:** [https://customer-churn-ml-api-6vvp.onrender.com](https://customer-churn-ml-api-6vvp.onrender.com)

> Note: free-tier hosting may "spin down" after inactivity — the first request after a period of no traffic can take up to \~60 seconds while the service wakes up.

If a live deployment isn't available, the project is fully reproducible locally with a single command:

```bash
docker compose up --build
```

\---

## Independent Extension

<!-- Document whichever Final Challenge option you actually built — replace this section -->

As the Final Challenge, this project was extended with **\[your chosen extension — e.g. "a GitHub Actions workflow that automatically runs the full pytest suite on every push and pull request to main"]**.

This was an independent decision beyond the guided tasks, chosen because **\[your reasoning — e.g. "it turns the test suite from something I remember to run manually into something that runs automatically, catching regressions before they reach main"]**.

See `.github/workflows/tests.yml` for the implementation.

\---

## What I Learned

<!-- Write this in your own words, based on real moments from building this project -->

Building this project end-to-end — not just training a model, but wrapping it in a real, versioned, authenticated, monitored, tested, and containerized service — taught me that most of the actual engineering work in an ML API isn't the model itself, it's everything around it: validating input before it ever reaches the model, tracing a single request through logs under concurrent load, and proving with a test (not just an assumption) that a change to one API version didn't silently break another.

A few specific moments stood out:

* **\[e.g. "Debugging why a missing API key returned 422 instead of the required 401 taught me that FastAPI's automatic validation happens before your own code runs — declaring a header as required vs. optional-with-manual-checking changes which layer handles the failure."]**
* **\[e.g. "My first load test revealed a \~14x latency increase under 100 concurrent requests, even though every request still succeeded — a reminder that 'it works' and 'it works under load' are genuinely different claims, and unit tests alone never surface the second one."]**
* **\[e.g. "Refactoring shared prediction logic into its own module before building /api/v2/predict, then re-running v1's existing tests to confirm nothing changed, made the difference between versioning 'in theory' and versioning I could actually prove was safe."]**

\---

## Monitoring and API Response Summary

The API provides information such as:

* Customer churn prediction (single or batch)
* Prediction confidence or full probability distribution, depending on API version
* Server-generated request ID, traceable through logs
* Model version metadata
* Health status
* Live Prometheus metrics, including a custom prediction-outcome counter

These details support API monitoring, debugging, and operational visibility in a way that goes beyond "the endpoint returned 200."

