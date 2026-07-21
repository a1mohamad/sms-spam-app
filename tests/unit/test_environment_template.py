from cryptography.fernet import Fernet
from dotenv import dotenv_values
import pytest

from app.core.config import PROJECT_ROOT


def test_environment_template_documents_required_database_settings() -> None:
    """Verify the template documents database and request-limit settings."""
    values = dotenv_values(PROJECT_ROOT / ".env.example")

    assert {
        "DB_PORT",
        "DB_CONNECT_TIMEOUT_SECONDS",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "MESSAGE_ENCRYPTION_KEY",
        "MAX_MESSAGE_LENGTH",
        "MAX_REQUEST_BODY_BYTES",
    }.issubset(values)
    assert str(values["DATABASE_URL"]).startswith(
        "postgresql+psycopg://"
    )


def test_environment_template_does_not_contain_a_real_encryption_key() -> None:
    values = dotenv_values(PROJECT_ROOT / ".env.example")
    example_key = values["MESSAGE_ENCRYPTION_KEY"]

    with pytest.raises((TypeError, ValueError)):
        Fernet(example_key)
