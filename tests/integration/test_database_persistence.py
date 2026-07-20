from collections.abc import Iterator

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from cryptography.fernet import Fernet
import pytest
from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.orm import Session

from app.core.config import AppConfig
from app.core.errors import PersistenceError
from app.repositories.prediction_repository import PredictionRepository
from app.security.message_cipher import MessageCipher


pytestmark = [pytest.mark.integration, pytest.mark.database]


@pytest.fixture(scope="module")
def database_engine() -> Iterator[Engine]:
    engine = create_engine(
        AppConfig.get_database_url(),
        pool_pre_ping=True,
        hide_parameters=True,
    )

    yield engine

    engine.dispose()


@pytest.fixture
def database_session(database_engine: Engine) -> Iterator[Session]:
    with Session(database_engine, expire_on_commit=False) as session:
        yield session
        session.rollback()


def test_database_is_at_alembic_head_with_expected_schema(
    database_engine: Engine,
) -> None:
    alembic_config = Config("alembic.ini")
    expected_revision = ScriptDirectory.from_config(
        alembic_config
    ).get_current_head()

    with database_engine.connect() as connection:
        current_revision = MigrationContext.configure(
            connection
        ).get_current_revision()

    assert current_revision == expected_revision

    inspector = inspect(database_engine)
    columns = {
        column["name"]: column
        for column in inspector.get_columns("predictions")
    }

    assert set(columns) == {
        "id",
        "message_ciphertext",
        "label",
        "spam_probability",
        "threshold",
        "message_length",
        "created_at",
    }
    assert all(not column["nullable"] for column in columns.values())
    assert str(columns["message_ciphertext"]["type"]) == "BYTEA"
    assert columns["created_at"]["default"] is not None
    assert inspector.get_pk_constraint("predictions")[
        "constrained_columns"
    ] == ["id"]
    assert {
        constraint["name"]
        for constraint in inspector.get_check_constraints("predictions")
    } == {
        "ck_predictions_label",
        "ck_predictions_message_length",
        "ck_predictions_spam_probability",
        "ck_predictions_threshold",
    }


def test_repository_round_trip_uses_ciphertext_and_rolls_back(
    database_session: Session,
) -> None:
    message = "Claim your prize – پاسخ دهید"
    cipher = MessageCipher(Fernet.generate_key().decode("utf-8"))
    repository = PredictionRepository(database_session)

    created = repository.create(
        message_ciphertext=cipher.encrypt(message),
        label="spam",
        spam_probability=0.91,
        threshold=0.5,
        message_length=len(message),
    )

    prediction_id = created.id
    assert prediction_id is not None
    assert created.created_at is not None
    assert created.message_ciphertext != message.encode("utf-8")

    database_session.expunge_all()
    retrieved = repository.get_by_id(prediction_id)

    assert retrieved is not None
    assert retrieved.label == "spam"
    assert retrieved.spam_probability == pytest.approx(0.91)
    assert cipher.decrypt(retrieved.message_ciphertext) == message

    database_session.rollback()
    assert repository.get_by_id(prediction_id) is None


@pytest.mark.parametrize(
    "invalid_values",
    [
        {"label": "unknown"},
        {"spam_probability": 1.01},
        {"threshold": -0.01},
        {"message_length": 0},
    ],
)
def test_repository_translates_database_constraint_failures(
    database_session: Session,
    invalid_values: dict[str, str | float | int],
) -> None:
    values = {
        "message_ciphertext": b"encrypted-message",
        "label": "ham",
        "spam_probability": 0.1,
        "threshold": 0.5,
        "message_length": 12,
    }
    values.update(invalid_values)
    repository = PredictionRepository(database_session)

    with pytest.raises(PersistenceError):
        repository.create(**values)

    database_session.rollback()
