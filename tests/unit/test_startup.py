from pathlib import Path
from unittest.mock import Mock

import pytest

from app.core.config import AppConfig
from app.core.startup import validate_artifact_paths, warmup_predictor
from app.ml.predictor import SpamPredictor

def test_validate_artifact_paths_raises_for_missing_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing_model_path = tmp_path / "missing-model.onnx"

    monkeypatch.setattr(
        AppConfig,
        "ONNX_MODEL_PATH",
        missing_model_path,
    )

    with pytest.raises(FileNotFoundError) as exc_info:
        validate_artifact_paths()

    assert str(missing_model_path) in str(exc_info.value)


def test_warmup_predictor_runs_initial_prediction() -> None:
    predictor = Mock(spec=SpamPredictor)

    warmup_predictor(predictor)

    predictor.predict.assert_called_once_with("Model warmup message")
