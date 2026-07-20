from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import PersistenceError
from app.db.models.prediction import Prediction


class PredictionRepository:
    """Create and retrieve persisted prediction records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: Active SQLAlchemy database session.
        """
        self._session = session

    def create(
        self,
        *,
        request_id: UUID,
        message_ciphertext: bytes,
        label: Literal["ham", "spam"],
        spam_probability: float,
        threshold: float,
        message_length: int,
    ) -> Prediction:
        """Create a prediction record without committing the transaction.

        Args:
            request_id: Correlation ID assigned to the API request.
            message_ciphertext: Encrypted SMS message.
            label: Predicted classification label.
            spam_probability: Model probability for the spam class.
            threshold: Classification threshold used by the model.
            message_length: Number of characters in the original message.

        Returns:
            Newly created prediction record.

        Raises:
            PersistenceError: If PostgreSQL rejects the record.
        """
        prediction = Prediction(
            request_id=request_id,
            message_ciphertext=message_ciphertext,
            label=label,
            spam_probability=spam_probability,
            threshold=threshold,
            message_length=message_length,
        )

        try:
            self._session.add(prediction)
            # Execute the INSERT and populate generated values such as the ID,
            # while leaving the final commit to the service layer.
            self._session.flush()
        except SQLAlchemyError as exc:
            raise PersistenceError(
                "Prediction persistence failed."
            ) from exc

        return prediction

    def get_by_id(self, prediction_id: int) -> Prediction | None:
        """Retrieve a prediction by its database ID.

        Args:
            prediction_id: Primary key of the prediction.

        Returns:
            Matching prediction, or None when it does not exist.

        Raises:
            PersistenceError: If the database query fails.
        """
        try:
            return self._session.get(Prediction, prediction_id)
        except SQLAlchemyError as exc:
            raise PersistenceError(
                "Prediction retrieval failed."
            ) from exc

    def get_by_request_id(self, request_id: UUID) -> Prediction | None:
        """Retrieve a prediction by its request correlation ID.

        Args:
            request_id: Correlation ID assigned to the API request.

        Returns:
            Matching prediction, or None when it does not exist.

        Raises:
            PersistenceError: If the database query fails.
        """
        statement = select(Prediction).where(
            Prediction.request_id == request_id
        )

        try:
            return self._session.scalar(statement)
        except SQLAlchemyError as exc:
            raise PersistenceError(
                "Prediction request lookup failed."
            ) from exc
