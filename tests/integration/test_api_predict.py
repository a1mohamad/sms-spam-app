from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from app.core.config import AppConfig
from app.db.models.prediction import Prediction
from app.main import app
from app.security.message_cipher import MessageCipher


pytestmark = [pytest.mark.integration, pytest.mark.database]


def test_app_predicts_and_persists_encrypted_message() -> None:
    """Exercise the complete HTTP, model, encryption, and database path."""
    message = "Congratulations, you won a free prize"
    request_id: UUID | None = None
    engine = create_engine(
        AppConfig.get_database_url(),
        pool_pre_ping=True,
        hide_parameters=True,
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/predict",
                json={"text": message},
            )

        assert response.status_code == 200
        result = response.json()
        assert result["label"] in ("ham", "spam")
        assert isinstance(result["spam_probability"], float)
        assert 0.0 <= result["spam_probability"] <= 1.0

        request_id = UUID(response.headers["x-request-id"])

        with Session(engine) as session:
            stored = session.scalar(
                select(Prediction).where(
                    Prediction.request_id == request_id
                )
            )

            assert stored is not None
            assert stored.request_id == request_id
            assert stored.label == result["label"]
            assert stored.spam_probability == pytest.approx(
                result["spam_probability"]
            )
            assert stored.threshold == pytest.approx(AppConfig.THRESHOLD)
            assert stored.message_length == len(message)
            assert stored.created_at is not None
            assert stored.message_ciphertext != message.encode("utf-8")

            cipher = MessageCipher(
                AppConfig.get_message_encryption_key()
            )
            assert cipher.decrypt(stored.message_ciphertext) == message
    finally:
        # The endpoint commits by design, so remove only the row created here.
        if request_id is not None:
            with Session(engine) as cleanup_session:
                cleanup_session.execute(
                    delete(Prediction).where(
                        Prediction.request_id == request_id
                    )
                )
                cleanup_session.commit()

        engine.dispose()
