import time
import uuid

from app.config import settings
from fastapi import APIRouter, HTTPException, Request
import pandas as pd

from app.logging_config import logger
from app.models.schemas import (
    PredictionInput, PredictionOutput,
    PredictionBatchInput, PredictionBatchOutput, ModelInfo,
)

router = APIRouter(prefix="/api/v1")

MODEL_VERSION = "1.0.0"
MODEL_TYPE = "LogisticRegression"
TRAINED_ON = "2026-08-20"
FEATURE_NAMES = [
    "Tenure Months", "Monthly Charges", "Total Charges", "Gender",
    "Senior Citizen", "Partner", "Dependents", "Phone Service",
    "Multiple Lines", "Internet Service", "Online Security",
    "Online Backup", "Device Protection", "Tech Support",
    "Streaming TV", "Streaming Movies", "Contract",
    "Paperless Billing", "Payment Method",
]


@router.get("/health")
def health(request: Request):
    app = request.app
    model_loaded = getattr(app.state, "model", None) is not None
    return {"status": "ok", "model_loaded": model_loaded}


@router.post("/predict", response_model=PredictionOutput)
def predict(customer: PredictionInput, request: Request):
    app = request.app
    request_id = request.state.request_id
    input_df = pd.DataFrame([customer.model_dump(by_alias=True)])

    try:
        model = app.state.model
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
    except Exception as e:
        logger.error(f"request_id={request_id} event=prediction_failed error={e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

    result = "Churn" if prediction == 1 else "No Churn"
    confidence = round(float(probability), 4)
    logger.info(
        f"request_id={request_id} event=prediction_success "
        f"prediction={result} confidence={confidence}"
    )
    return {
        "prediction": result,
        "confidence": confidence,
        "model_version": MODEL_VERSION,
        "request_id": request_id,
    }


@router.get("/model-info", response_model=ModelInfo)
def model_info():
    return {
        "model_type": MODEL_TYPE,
        "model_version": MODEL_VERSION,
        "trained_on": TRAINED_ON,
        "features": FEATURE_NAMES,
    }


@router.post("/predict-batch", response_model=PredictionBatchOutput)
def predict_batch(batch: PredictionBatchInput, request: Request):
    app = request.app
    request_id = request.state.request_id

    if len(batch.customers) > settings.MAX_BATCH_SIZE:
        logger.error(
            f"request_id={request_id} event=batch_size_exceeded "
            f"batch_size={len(batch.customers)} max_allowed={settings.MAX_BATCH_SIZE}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Batch size {len(batch.customers)} exceeds maximum allowed ({settings.MAX_BATCH_SIZE})",
        )

    start_time = time.time()
    input_df = pd.DataFrame(
        [c.model_dump(by_alias=True) for c in batch.customers]
    )

    try:
        model = app.state.model
        predictions = model.predict(input_df)
        probabilities = model.predict_proba(input_df)[:, 1]
    except Exception as e:
        logger.error(f"request_id={request_id} event=batch_prediction_failed error={e}")
        raise HTTPException(status_code=500, detail="Batch prediction failed")

    results = [
        {
            "prediction": "Churn" if pred == 1 else "No Churn",
            "confidence": round(float(proba), 4),
            "model_version": MODEL_VERSION,
            "request_id": str(uuid.uuid4()),
        }
        for pred, proba in zip(predictions, probabilities)
    ]

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"request_id={request_id} event=batch_prediction_success "
        f"batch_size={len(batch.customers)} duration_ms={duration_ms}"
    )

    return {
        "predictions": results,
        "batch_size": len(batch.customers),
        "request_id": request_id,
    }
