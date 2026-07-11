from app.core.config import AppConfig
from app.utils.artifact_io import open_json_file


def test_required_runtime_artifacts_exist():
    assert AppConfig.ONNX_MODEL_PATH.exists()
    assert AppConfig.VOCAB_PATH.exists()
    assert AppConfig.LABEL_MAPPING_PATH.exists()


def test_vocab_artifact_has_required_keys():
    vocabs_artifact = open_json_file(AppConfig.VOCAB_PATH)

    assert "vocabs" in vocabs_artifact
    assert "output_sequence_length" in vocabs_artifact


def test_label_mapping_artifact_has_expected_classes():
    label_mapping_artifact = open_json_file(AppConfig.LABEL_MAPPING_PATH)

    assert label_mapping_artifact == {
        "0": "ham",
        "1": "spam",
    }