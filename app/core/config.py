import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load local development settings before AppConfig evaluates os.getenv calls.
# Existing process variables take precedence, as they should in deployment.
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)


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
    BASE_DIR: Path = PROJECT_ROOT
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


    @staticmethod
    def get_database_url() -> str:
        """Load and normalize the database connection URL.

        Returns:
            str: A SQLAlchemy URL configured for Psycopg 3.

        Raises:
            RuntimeError: If DATABASE_URL is missing.
        """

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is required."
            )
        
        if database_url.startswith("postgres://"):
            return database_url.replace(
                "postgres://",
                "postgresql+psycopg://",
                1,
            )
        if database_url.startswith("postgresql://"):
            return database_url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )
        
        return database_url
