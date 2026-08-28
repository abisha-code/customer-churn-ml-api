import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import uuid
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import PredictionInput, PredictionOutput

MODEL_PATH = "ml/saved_model/model.joblib"
MODEL_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
    yield
    print("Shutting down. Model unloaded.")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    print(f"ValueError occurred: {exc}")
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
def predict(customer: PredictionInput):
    input_df = pd.DataFrame([customer.model_dump(by_alias=True)])

    try:
        model = app.state.model
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
    except Exception as e:
        print(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

    return {
        "prediction": "Churn" if prediction == 1 else "No Churn",
        "confidence": round(float(probability), 4),
        "model_version": MODEL_VERSION,
        "request_id": str(uuid.uuid4()),
    }



