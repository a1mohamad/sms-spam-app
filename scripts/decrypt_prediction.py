from sqlalchemy.orm import Session

from app.db.models.prediction import Prediction
from app.security.message_cipher import MessageCipher


def get_decrypted_message(
    prediction_id: int,
    session: Session,
    cipher: MessageCipher,
) -> str:
    """Retrieve and decrypt a stored SMS message.

    Args:
        prediction_id: Database ID of the prediction.
        session: Active SQLAlchemy database session.
        cipher: Configured message cipher.

    Returns:
        Decrypted SMS message.

    Raises:
        LookupError: If the prediction does not exist.
        MessageDecryptionError: If decryption fails.
    """
    prediction = session.get(Prediction, prediction_id)

    if prediction is None:
        raise LookupError(
            f"Prediction {prediction_id} does not exist."
        )

    return cipher.decrypt(prediction.message_ciphertext)