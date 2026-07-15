from pathlib import Path

import numpy as np
import onnxruntime as ort

from app.core.config import AppConfig
from app.core.errors import PredictionError
from app.ml.preprocessing import Preprocessor
from app.utils.artifact_io import open_json_file


class SpamPredictor:
    """Runtime predictor for classifying SMS messages as ham or spam.

    The predictor loads the preprocessing vocabulary, ONNX model, and label
    mapping artifacts once during initialization. Prediction then accepts raw
    SMS text, converts it to token IDs, runs ONNX inference, and maps the model
    score to a human-readable class label.

    TensorFlow is intentionally not imported here so the deployment runtime
    stays lightweight.
    """

    def __init__(
        self,
        model_path: Path = AppConfig.ONNX_MODEL_PATH,
        label_mapping_path: Path = AppConfig.LABEL_MAPPING_PATH,
        threshold: float = AppConfig.THRESHOLD,
        vocab_path: Path = AppConfig.VOCAB_PATH,
    ) -> None:
        """Load model and preprocessing artifacts.

        Args:
            model_path: Path to the exported ONNX model file.
            label_mapping_path: Path to the JSON file mapping class IDs to names.
            threshold: Minimum spam probability required to predict "spam".
            vocab_path: Path to the vocabulary/preprocessing artifact.
        """
        self.preprocessor = Preprocessor(vocab_path=vocab_path)
        self.session = ort.InferenceSession(str(model_path))
        self.input_name = self.session.get_inputs()[0].name
        self.label_mapping: dict[str, str] = open_json_file(label_mapping_path)
        self.threshold = threshold

    def predict(self, text: str) -> dict[str, str | float]:
        """Classify raw SMS text.

        Args:
            text: Raw SMS message text.

        Returns:
            Dictionary containing:
                label: Predicted class label, usually "ham" or "spam".
                spam_probability: Model score for the spam class.
        """
        token_ids = self.preprocessor.tokenize(text)

        # Treat failures from the external ONNX runtime as a known service
        # failure so the API can return a safe, retryable response.
        try:
            outputs = self.session.run(None, {self.input_name: token_ids})
        except Exception as exc:
            raise PredictionError("ONNX inference failed") from exc

        # ONNX returns a batched array such as [[0.63]]; flatten it to one score.
        spam_prob = float(np.ravel(outputs[0])[0])

        return {
            "label": self.label_from_probability(spam_prob),
            "spam_probability": spam_prob,
        }

    def label_from_probability(self, spam_probability: float) -> str:
        """Map a spam probability score to a class label.

        Args:
            spam_probability: Model score for the spam class.

        Returns:
            Predicted class label from the label mapping.
        """
        class_id = "1" if spam_probability >= self.threshold else "0"
        return self.label_mapping[class_id]
