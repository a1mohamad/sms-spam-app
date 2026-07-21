from pathlib import Path

import pytest

from app.core.config import AppConfig


def test_artifact_paths_are_path_objects():
    assert isinstance(AppConfig.ONNX_MODEL_PATH, Path)
    assert isinstance(AppConfig.VOCAB_PATH, Path)
    assert isinstance(AppConfig.LABEL_MAPPING_PATH, Path)


def test_artifact_paths_have_expected_suffixes():
    assert AppConfig.ONNX_MODEL_PATH.suffix == ".onnx"
    assert AppConfig.VOCAB_PATH.suffix == ".json"
    assert AppConfig.LABEL_MAPPING_PATH.suffix == ".json"


def test_threshold_is_valid_probability():
    assert 0.0 <= AppConfig.THRESHOLD <= 1.0


def test_max_length_is_positive_integer():
    assert isinstance(AppConfig.MAX_LENGTH, int)
    assert AppConfig.MAX_LENGTH > 0


def test_request_limits_are_positive_and_coherent():
    """Verify request limits are positive and leave room for JSON overhead."""
    assert AppConfig.MAX_MESSAGE_LENGTH > 0
    assert AppConfig.MAX_REQUEST_BODY_BYTES > AppConfig.MAX_MESSAGE_LENGTH


def test_database_connect_timeout_is_positive():
    """Verify database connection waits have a positive upper bound."""
    assert AppConfig.DB_CONNECT_TIMEOUT_SECONDS > 0


@pytest.mark.parametrize(
    ("configured_url", "expected_url"),
    [
        (
            "postgres://user:password@localhost:5432/database",
            "postgresql+psycopg://user:password@localhost:5432/database",
        ),
        (
            "postgresql://user:password@localhost:5432/database",
            "postgresql+psycopg://user:password@localhost:5432/database",
        ),
        (
            "postgresql+psycopg://user:password@localhost:5432/database",
            "postgresql+psycopg://user:password@localhost:5432/database",
        ),
    ],
)
def test_database_url_uses_psycopg_driver(
    monkeypatch: pytest.MonkeyPatch,
    configured_url: str,
    expected_url: str,
) -> None:
    monkeypatch.setenv("DATABASE_URL", configured_url)

    assert AppConfig.get_database_url() == expected_url


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        AppConfig.get_database_url()


def test_message_encryption_key_is_trimmed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MESSAGE_ENCRYPTION_KEY", "  test-key  ")

    assert AppConfig.get_message_encryption_key() == "test-key"


def test_message_encryption_key_is_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MESSAGE_ENCRYPTION_KEY", raising=False)

    with pytest.raises(RuntimeError, match="MESSAGE_ENCRYPTION_KEY"):
        AppConfig.get_message_encryption_key()
