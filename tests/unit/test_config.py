from pathlib import Path

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