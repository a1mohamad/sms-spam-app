from collections.abc import Iterator
import json
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient
import pytest

import app.main as main_module
from app.ml.predictor import SpamPredictor
from app.ml.preprocessing import Preprocessor


@pytest.fixture
def fake_vocab_path(tmp_path: Path) -> Path:
    """Create a temporary vocabulary artifact for preprocessor tests."""
    vocab_artifact = {
        "vocabs": ["", "[UNK]", "hello", "free", "prize", "claim", "now"],
        "output_sequence_length": 100,
    }

    path = tmp_path / "vocabs_config.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(vocab_artifact, f)

    return path


@pytest.fixture
def preprocessor(fake_vocab_path: Path) -> Preprocessor:
    """Create a preprocessor backed by the temporary test vocabulary."""
    return Preprocessor(vocab_path=fake_vocab_path)


@pytest.fixture
def mock_predictor() -> Mock:
    """Create a predictor mock with a stable response."""
    predictor = Mock(spec=SpamPredictor)
    predictor.predict.return_value = {
        "label": "spam",
        "spam_probability": 0.9,
    }

    return predictor


@pytest.fixture
def api_client(
    monkeypatch: pytest.MonkeyPatch,
    mock_predictor: Mock,
) -> Iterator[TestClient]:
    """Create an API client using a mocked predictor.

    Args:
        monkeypatch: Pytest fixture for replacing the predictor factory.
        mock_predictor: Mocked predictor used by the application.

    Yields:
        Test client with application lifespan enabled.
    """
    monkeypatch.setattr(
        main_module,
        "create_predictor",
        lambda: mock_predictor,
    )

    with TestClient(main_module.app) as client:
        # Exclude the prediction performed during application warmup.
        mock_predictor.predict.reset_mock()
        yield client