from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import MessageEncryptionError, PersistenceError
from app.db.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository
from app.security.message_cipher import MessageCipher
from app.services.prediction_service import PredictionService


def make_service() -> tuple[
    PredictionService,
    Mock,
    Mock,
    Mock,
]:
    session = Mock(spec=Session)
    repository = Mock(spec=PredictionRepository)
    message_cipher = Mock(spec=MessageCipher)
    service = PredictionService(
        session=session,
        repository=repository,
        message_cipher=message_cipher,
    )
    return service, session, repository, message_cipher


def test_save_prediction_encrypts_persists_and_commits() -> None:
    service, session, repository, message_cipher = make_service()
    request_id = uuid4()
    message = "سلام"
    ciphertext = b"encrypted-message"
    expected = Prediction(
        request_id=request_id,
        message_ciphertext=ciphertext,
        label="ham",
        spam_probability=0.1,
        threshold=0.5,
        message_length=len(message),
    )
    message_cipher.encrypt.return_value = ciphertext
    repository.create.return_value = expected

    result = service.save_prediction(
        request_id=request_id,
        message=message,
        label="ham",
        spam_probability=0.1,
        threshold=0.5,
    )

    assert result is expected
    message_cipher.encrypt.assert_called_once_with(message)
    repository.create.assert_called_once_with(
        request_id=request_id,
        message_ciphertext=ciphertext,
        label="ham",
        spam_probability=0.1,
        threshold=0.5,
        message_length=4,
    )
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


def test_save_prediction_rolls_back_repository_failure() -> None:
    service, session, repository, message_cipher = make_service()
    error = PersistenceError("safe persistence failure")
    message_cipher.encrypt.return_value = b"encrypted-message"
    repository.create.side_effect = error

    with pytest.raises(PersistenceError) as exc_info:
        service.save_prediction(
            request_id=uuid4(),
            message="message",
            label="spam",
            spam_probability=0.9,
            threshold=0.5,
        )

    assert exc_info.value is error
    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()


def test_save_prediction_translates_commit_failure() -> None:
    service, session, repository, message_cipher = make_service()
    database_error = SQLAlchemyError("database implementation detail")
    message_cipher.encrypt.return_value = b"encrypted-message"
    repository.create.return_value = Mock(spec=Prediction)
    session.commit.side_effect = database_error

    with pytest.raises(PersistenceError) as exc_info:
        service.save_prediction(
            request_id=uuid4(),
            message="message",
            label="ham",
            spam_probability=0.1,
            threshold=0.5,
        )

    assert exc_info.value.__cause__ is database_error
    assert "implementation detail" not in str(exc_info.value)
    session.rollback.assert_called_once_with()


def test_save_prediction_stops_before_database_when_encryption_fails() -> None:
    service, session, repository, message_cipher = make_service()
    error = MessageEncryptionError("safe encryption failure")
    message_cipher.encrypt.side_effect = error

    with pytest.raises(MessageEncryptionError) as exc_info:
        service.save_prediction(
            request_id=uuid4(),
            message="private message",
            label="ham",
            spam_probability=0.1,
            threshold=0.5,
        )

    assert exc_info.value is error
    repository.create.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
