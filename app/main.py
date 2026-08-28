import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time
import uuid
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionOutput

MODEL_PATH = "ml/saved_model/model.joblib"
MODEL_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
    yield
    logger.info("Shutting down. Model unloaded.")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"request_id={request_id} method={request.method} path={request.url.path} "
        f"status_code={response.status_code} duration_ms={duration_ms}"
    )

    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"request_id={request_id} event=value_error error={exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid data encountered during prediction. Please check your input values."},
    )


@app.get("/")
def root():
    return {"message": "ML API is alive"}


@app.get("/health")
def health():
    model_loaded = getattr(app.state, "model", None) is not None
    return {"status": "ok", "model_loaded": model_loaded}


@app.post("/predict", response_model=PredictionOutput)
def predict(customer: PredictionInput, request: Request):
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
