import uuid
from fastapi import APIRouter, Request
from app.models.schemas import PredictionInput, PredictionOutputV2
from app.services.prediction_service import run_prediction

router = APIRouter(prefix="/api/v2")
MODEL_VERSION = "2.0.0"


@router.post("/predict", response_model=PredictionOutputV2)
def predict(customer: PredictionInput, request: Request):
    app = request.app
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    model = app.state.model
    pred, proba_churn = run_prediction(model, customer)

    return {
        "prediction": "Churn" if pred == 1 else "No Churn",
        "probabilities": {
            "Churn": round(proba_churn, 4),
            "No Churn": round(1 - proba_churn, 4),
        },
        "model_version": MODEL_VERSION,
        "request_id": request_id,
    }
