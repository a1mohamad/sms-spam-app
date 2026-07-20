from unittest.mock import Mock

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db.session import Database


def make_database_with_session(session: Mock) -> Database:
    database = Database.__new__(Database)
    database._session_factory = Mock(return_value=session)
    return database


def test_database_closes_successful_session() -> None:
    session = Mock(spec=Session)
    database = make_database_with_session(session)
    session_generator = database.get_session()

    assert next(session_generator) is session

    session_generator.close()

    session.rollback.assert_not_called()
    session.close.assert_called_once_with()


def test_database_rolls_back_and_closes_failed_session() -> None:
    session = Mock(spec=Session)
    database = make_database_with_session(session)
    session_generator = database.get_session()
    next(session_generator)

    with pytest.raises(RuntimeError, match="request failed"):
        session_generator.throw(RuntimeError("request failed"))

    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()


def test_database_dispose_closes_engine_connections() -> None:
    engine = Mock(spec=Engine)
    database = Database.__new__(Database)
    database._engine = engine

    database.dispose()

    engine.dispose.assert_called_once_with()
