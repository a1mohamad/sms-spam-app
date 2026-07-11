import os
from pathlib import Path


class AppConfig:
    """Application configuration for training, artifacts, and inference.

    Configuration values are class attributes so they can be imported anywhere
    in the project without creating an instance. Runtime paths and inference
    settings can be overridden with environment variables, which is useful for
    tests and deployment.
    """

    # Reproducibility.
    SEED: int = 28

    # Project paths.
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    ARTIFACTS_DIR: Path = Path(
        os.getenv("ARTIFACTS_DIR", BASE_DIR / "artifacts")
    )

    # Model artifact paths.
    MODEL_PATH: Path = Path(
        os.getenv("MODEL_PATH", ARTIFACTS_DIR / "sms-spam-model.keras")
    )
    ONNX_MODEL_PATH: Path = Path(
        os.getenv("ONNX_MODEL_PATH", ARTIFACTS_DIR / "sms-spam-model.onnx")
    )
    VOCAB_PATH: Path = Path(
        os.getenv("VOCAB_PATH", ARTIFACTS_DIR / "vocabs_config.json")
    )
    LABEL_MAPPING_PATH: Path = Path(
        os.getenv("LABEL_MAPPING_PATH", ARTIFACTS_DIR / "label_mapping.json")
    )

    # Model architecture/training settings.
    EMB_DIM: int = 16
    LSTM_UNIT: int = 16
    DROPOUT: float = 0.444
    HIDDEN_LAYER: int = 128
    ONNX_OPSET_VERSION: int = 13

    # Runtime inference settings.
    MAX_LENGTH: int = int(os.getenv("MAX_LENGTH", "100"))
    THRESHOLD: float = float(os.getenv("THRESHOLD", "0.5"))