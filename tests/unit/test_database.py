from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import DatabaseUnavailableError
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


def test_database_health_check_executes_query() -> None:
    """Verify readiness performs a real query on a checked-out connection."""
    engine = Mock(spec=Engine)
    connection_context = MagicMock()
    engine.connect.return_value = connection_context
    connection = connection_context.__enter__.return_value
    database = Database.__new__(Database)
    database._engine = engine

    database.check_connection()

    connection.execute.assert_called_once()


def test_database_health_check_translates_sqlalchemy_error() -> None:
    """Verify readiness hides SQLAlchemy connection details from callers."""
    engine = Mock(spec=Engine)
    engine.connect.side_effect = SQLAlchemyError("sensitive database detail")
    database = Database.__new__(Database)
    database._engine = engine

    with pytest.raises(DatabaseUnavailableError) as exc_info:
        database.check_connection()

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)
    assert "sensitive" not in str(exc_info.value)
