from pathlib import Path

from app.core.config import AppConfig
from app.ml.predictor import SpamPredictor


def validate_artifact_paths() -> None:
    """Ensure all artifacts required for runtime inference are files.

    Raises:
        FileNotFoundError: If one or more required runtime artifacts are
            missing or are not regular files.
    """
    required_paths: tuple[Path, ...] = (
        AppConfig.ONNX_MODEL_PATH,
        AppConfig.VOCAB_PATH,
        AppConfig.LABEL_MAPPING_PATH,
    )

    missing_paths = [path for path in required_paths if not path.is_file()]

    if missing_paths:
        formatted_paths = ", ".join(str(path) for path in missing_paths)
        raise FileNotFoundError(
            f"Required runtime artifacts are missing: {formatted_paths}"
        )


def create_predictor() -> SpamPredictor:
    """Create the process-wide spam predictor.

    Returns:
        Initialized spam predictor with its runtime artifacts loaded.
    """
    return SpamPredictor()


def warmup_predictor(predictor: SpamPredictor) -> None:
    """Run an initial prediction before serving traffic.

    Args:
        predictor: Spam predictor instance to warm up.
    """
    predictor.predict("Model warmup message")