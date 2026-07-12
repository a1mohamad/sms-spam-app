from fastapi import APIRouter, Request

from app.api.schemas import PredictRequest, PredictionResponse
from app.ml.predictor import SpamPredictor


router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    """Return basic information about the API.

    Returns:
        Dictionary containing API metadata.
    """
    return {
        "name": "SMS Spam Classifier",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status.

    Returns:
        Dictionary containing the API health status.
    """
    return {"status": "ok"}


@router.post("/predict")
def predict(
    payload: PredictRequest,
    request: Request,
) -> PredictionResponse:
    """Classify an SMS message as ham or spam.

    Args:
        payload: Validated SMS prediction request.
        request: Current request containing the application state.

    Returns:
        Predicted label and spam probability.
    """
    predictor: SpamPredictor = request.app.state.predictor
    result = predictor.predict(payload.text)

    return PredictionResponse.model_validate(result)