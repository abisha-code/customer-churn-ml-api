"""
Task 3 — Prove the saved pipeline can be reloaded and used without retraining.
"""

import joblib
import pandas as pd

# 1. Load the saved pipeline
pipeline = joblib.load("ml/saved_model/model.joblib")
print("Loaded pipeline successfully:", type(pipeline))

# 2. Build one sample customer record

sample_customer = pd.DataFrame([{
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
}])

# 3. Predict
prediction = pipeline.predict(sample_customer)[0]
confidence = pipeline.predict_proba(sample_customer)[0][1]

label = "Churn" if prediction == 1 else "No Churn"
print(f"Prediction: {label}")
print(f"Confidence (probability of churn): {confidence:.4f}")
