import json
from pathlib import Path

import pytest

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