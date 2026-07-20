from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import PersistenceError
from app.db.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository


def make_repository() -> tuple[PredictionRepository, Mock]:
    session = Mock(spec=Session)
    return PredictionRepository(session), session


def test_create_adds_and_flushes_prediction() -> None:
    repository, session = make_repository()

    created = repository.create(
        message_ciphertext=b"encrypted-message",
        label="spam",
        spam_probability=0.9,
        threshold=0.5,
        message_length=12,
    )

    session.add.assert_called_once_with(created)
    session.flush.assert_called_once_with()
    assert created.message_ciphertext == b"encrypted-message"
    assert created.label == "spam"
    assert created.spam_probability == 0.9
    assert created.threshold == 0.5
    assert created.message_length == 12


def test_create_translates_sqlalchemy_error() -> None:
    repository, session = make_repository()
    session.flush.side_effect = SQLAlchemyError("database detail")

    with pytest.raises(PersistenceError) as exc_info:
        repository.create(
            message_ciphertext=b"encrypted-message",
            label="ham",
            spam_probability=0.1,
            threshold=0.5,
            message_length=12,
        )

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)
    assert "database detail" not in str(exc_info.value)


def test_get_by_id_returns_session_result() -> None:
    repository, session = make_repository()
    expected = Prediction(
        message_ciphertext=b"encrypted-message",
        label="ham",
        spam_probability=0.1,
        threshold=0.5,
        message_length=12,
    )
    session.get.return_value = expected

    result = repository.get_by_id(42)

    assert result is expected
    session.get.assert_called_once_with(Prediction, 42)


def test_get_by_id_translates_sqlalchemy_error() -> None:
    repository, session = make_repository()
    session.get.side_effect = SQLAlchemyError("database detail")

    with pytest.raises(PersistenceError) as exc_info:
        repository.get_by_id(42)

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)
    assert "database detail" not in str(exc_info.value)
