"""Validate prediction parity between the Keras model and exported ONNX model.

This script is part of the offline model packaging workflow. It loads the
trained Keras artifact and exported ONNX artifact, runs both models on the same
preprocessed sample SMS messages, and verifies that their outputs are close
within a small numerical tolerance.

TensorFlow is imported lazily inside `load_keras_model()` so normal runtime
imports do not accidentally pull TensorFlow into deployment code.
"""

import os
import sys
from pathlib import Path

# Must happen before TensorFlow is imported.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import onnxruntime as ort

from app.core.config import AppConfig
from app.ml.preprocessing import Preprocessor


RTOL: float = 1e-4
ATOL: float = 1e-4


def load_keras_model():
    """Load the trained Keras model artifact.

    Returns:
        The loaded TensorFlow/Keras model.
    """
    import tensorflow as tf

    return tf.keras.models.load_model(
        AppConfig.MODEL_PATH,
        compile=False,
    )


def validate_keras_onnx_parity() -> None:
    """Assert that Keras and ONNX predictions are numerically close."""
    keras_model = load_keras_model()

    onnx_session = ort.InferenceSession(str(AppConfig.ONNX_MODEL_PATH))
    onnx_input_name = onnx_session.get_inputs()[0].name

    preprocessor = Preprocessor(vocab_path=AppConfig.VOCAB_PATH)

    samples = [
        "Hey, are we still meeting today?",
        "Congratulations you won a free prize claim now",
        "Call me when you get home",
        "URGENT! You have won cash, reply now",
        "Can you send me the document later?",
    ]

    max_abs_diff = 0.0

    for text in samples:
        x = preprocessor.tokenize(text)

        keras_output = keras_model.predict(x, verbose=0)
        onnx_output = onnx_session.run(None, {onnx_input_name: x})[0]

        diff = np.max(np.abs(keras_output - onnx_output))
        max_abs_diff = max(max_abs_diff, float(diff))

        np.testing.assert_allclose(
            onnx_output,
            keras_output,
            rtol=RTOL,
            atol=ATOL,
        )

    print("Keras and ONNX outputs are close.")
    print(f"Max absolute difference: {max_abs_diff:.8f}")


if __name__ == "__main__":
    validate_keras_onnx_parity()