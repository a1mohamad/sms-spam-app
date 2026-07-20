from collections.abc import Iterator
import json
from pathlib import Path
from unittest.mock import Mock, create_autospec

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
import pytest

import app.main as main_module
from app.core.config import AppConfig
from app.ml.predictor import SpamPredictor
from app.ml.preprocessing import Preprocessor
from app.services.prediction_service import PredictionService


@pytest.fixture
def fake_vocab_path(tmp_path: Path) -> Path:
    """Create a temporary vocabulary artifact for preprocessor tests."""
    vocab_artifact = {
        "vocabs": [
            "",
            "[UNK]",
            "hello",
            "free",
            "prize",
            "claim",
            "now",
        ],
        "output_sequence_length": 100,
    }

    path = tmp_path / "vocabs_config.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(vocab_artifact, file)

    return path


@pytest.fixture
def preprocessor(fake_vocab_path: Path) -> Preprocessor:
    """Create a preprocessor backed by the test vocabulary.

    Args:
        fake_vocab_path: Path to the temporary vocabulary artifact.

    Returns:
        Configured text preprocessor.
    """
    return Preprocessor(vocab_path=fake_vocab_path)


@pytest.fixture
def mock_predictor() -> Mock:
    """Create a predictor double matching the production interface.

    Returns:
        Predictor mock with stable threshold and prediction output.
    """
    predictor = create_autospec(
        SpamPredictor,
        instance=True,
    )

    # Reuse the application's configured threshold instead of duplicating it.
    predictor.threshold = AppConfig.THRESHOLD
    predictor.predict.return_value = {
        "label": "spam",
        "spam_probability": 0.9,
    }

    return predictor


@pytest.fixture
def mock_save_prediction(
    monkeypatch: pytest.MonkeyPatch,
) -> Mock:
    """Replace prediction persistence with an observable test double.

    Args:
        monkeypatch: Pytest fixture for replacing service behavior.

    Returns:
        Mocked save method used by API assertions.
    """
    save_prediction = Mock(name="save_prediction")

    monkeypatch.setattr(
        PredictionService,
        "save_prediction",
        save_prediction,
    )

    return save_prediction


@pytest.fixture
def api_message_encryption_key(
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    """Provide a fresh Fernet key for each API test.

    Args:
        monkeypatch: Pytest fixture for replacing configuration behavior.

    Returns:
        Generated Fernet key used only by the current test.
    """
    encryption_key = Fernet.generate_key().decode("utf-8")

    # API tests should not depend on a developer's private .env file.
    monkeypatch.setattr(
        AppConfig,
        "get_message_encryption_key",
        staticmethod(lambda: encryption_key),
    )

    return encryption_key


@pytest.fixture
def api_client(
    monkeypatch: pytest.MonkeyPatch,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
    api_message_encryption_key: str,
) -> Iterator[TestClient]:
    """Create an isolated API client with mocked runtime dependencies.

    Args:
        monkeypatch: Pytest fixture for replacing the predictor factory.
        mock_predictor: Predictor double used by the application.
        mock_save_prediction: Mock preventing real database writes.
        api_message_encryption_key: Temporary key used during startup.

    Yields:
        API client with application lifespan enabled.
    """
    monkeypatch.setattr(
        main_module,
        "create_predictor",
        lambda: mock_predictor,
    )

    with TestClient(main_module.app) as client:
        # Exclude the prediction performed during application warmup.
        mock_predictor.predict.reset_mock()
        mock_save_prediction.reset_mock()

        yield client


@pytest.fixture
def error_api_client(
    monkeypatch: pytest.MonkeyPatch,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
    api_message_encryption_key: str,
) -> Iterator[TestClient]:
    """Create an isolated client that exposes handled HTTP errors.

    Args:
        monkeypatch: Pytest fixture for replacing the predictor factory.
        mock_predictor: Predictor double configured by each error test.
        mock_save_prediction: Mock preventing real database writes.
        api_message_encryption_key: Temporary key used during startup.

    Yields:
        Client returning handled errors instead of re-raising exceptions.
    """
    monkeypatch.setattr(
        main_module,
        "create_predictor",
        lambda: mock_predictor,
    )

    with TestClient(
        main_module.app,
        raise_server_exceptions=False,
    ) as client:
        # Tests configure failures after the successful startup warmup.
        mock_predictor.predict.reset_mock()
        mock_save_prediction.reset_mock()

        yield client