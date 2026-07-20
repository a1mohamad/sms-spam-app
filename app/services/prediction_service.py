from typing import Literal
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import PersistenceError
from app.db.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository
from app.security.message_cipher import MessageCipher


class PredictionService:
    """Coordinate encrypted prediction persistence and transactions."""

    def __init__(
        self,
        *,
        session: Session,
        repository: PredictionRepository,
        message_cipher: MessageCipher,
    ) -> None:
        """Initialize the prediction service.

        Args:
            session: Active SQLAlchemy database session.
            repository: Prediction database repository.
            message_cipher: Service used to encrypt SMS content.
        """
        self._session = session
        self._repository = repository
        self._message_cipher = message_cipher

    def save_prediction(
        self,
        *,
        request_id: UUID,
        message: str,
        label: Literal["ham", "spam"],
        spam_probability: float,
        threshold: float,
    ) -> Prediction:
        """Encrypt and permanently save a prediction.

        Args:
            request_id: Correlation ID assigned to the API request.
            message: Plaintext SMS message.
            label: Predicted classification label.
            spam_probability: Model probability for the spam class.
            threshold: Classification threshold used by the model.

        Returns:
            Committed prediction record.

        Raises:
            MessageEncryptionError: If message encryption fails.
            PersistenceError: If the database transaction fails.
        """
        # Plaintext exists only in application memory and is never given to
        # the repository.
        ciphertext = self._message_cipher.encrypt(message)

        try:
            prediction = self._repository.create(
                request_id=request_id,
                message_ciphertext=ciphertext,
                label=label,
                spam_probability=spam_probability,
                threshold=threshold,
                message_length=len(message),
            )

            # Make the inserted prediction permanent.
            self._session.commit()

        except PersistenceError:
            self._session.rollback()
            raise
        except SQLAlchemyError as exc:
            # Commit failures happen outside the repository and must also be
            # translated into the application's safe persistence exception.
            self._session.rollback()
            raise PersistenceError(
                "Prediction transaction failed."
            ) from exc

        return prediction
