import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI

from app.models.schemas import PredictionInput

MODEL_PATH = "ml/saved_model/model.joblib"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
    yield
    print("Shutting down. Model unloaded.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "ML API is alive"}


@app.post("/predict")
def predict(customer: PredictionInput):
    input_df = pd.DataFrame([customer.model_dump(by_alias=True)])

    model = app.state.model
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    return {
        "prediction": "Churn" if prediction == 1 else "No Churn",
        "confidence": round(float(probability), 4),
    }
