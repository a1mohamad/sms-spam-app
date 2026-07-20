from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.schemas import PredictRequest, PredictionResponse
from app.db.session import database
from app.ml.predictor import SpamPredictor
from app.repositories.prediction_repository import PredictionRepository
from app.security.message_cipher import MessageCipher
from app.services.prediction_service import PredictionService

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
    session: Annotated[
        Session,
        Depends(database.get_session),
    ],
) -> PredictionResponse:
    """Classify an SMS and persist its encrypted prediction.

    Args:
        payload: Validated SMS prediction request.
        request: Current request containing application runtime services.
        session: Request-scoped SQLAlchemy database session.

    Returns:
        Predicted label and spam probability.
    """
    predictor: SpamPredictor = request.app.state.predictor
    message_cipher: MessageCipher = request.app.state.message_cipher

    # Validate the predictor contract before attempting persistence.
    result = PredictionResponse.model_validate(
        predictor.predict(payload.text)
    )

    repository = PredictionRepository(session=session)
    service = PredictionService(
        session=session,
        repository=repository,
        message_cipher=message_cipher,
    )

    service.save_prediction(
        request_id=UUID(request.state.request_id),
        message=payload.text,
        label=result.label,
        spam_probability=result.spam_probability,
        threshold=predictor.threshold,
    )
    
    return result