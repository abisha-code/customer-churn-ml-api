import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"


from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI

MODEL_PATH = "ml/saved_model/model.joblib"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load the trained pipeline ONCE
    app.state.model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")

    yield  
    print("Shutting down. Model unloaded.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "ML API is alive"}


@app.post("/predict")
def predict():
    customer = pd.DataFrame([{
        "Tenure Months": 60,
        "Monthly Charges": 75.50,
        "Total Charges": 906.00,
        "Gender": "Female",
        "Senior Citizen": "Yes",
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
    }])

    model = app.state.model

    prediction = model.predict(customer)[0]          # 0 or 1
    probability = model.predict_proba(customer)[0][1]  # P(churn)

    return {
        "prediction": "Churn" if prediction == 1 else "No Churn",
        "confidence": round(float(probability), 4),
    }
