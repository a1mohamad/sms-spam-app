"""Convert the trained Keras SMS spam model to ONNX format.

This script is part of the offline model packaging workflow. It loads the
trained `.keras` model artifact, exports it to ONNX, and writes the result to
the configured ONNX model path.

TensorFlow and tf2onnx are intentionally imported only in this conversion
script so the runtime predictor can stay lightweight.
"""

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf
import tf2onnx

from app.core.config import AppConfig


def convert_to_onnx() -> None:
    """Export the configured Keras model artifact to ONNX format."""
    model = tf.keras.models.load_model(AppConfig.MODEL_PATH)

    input_signature = [
        tf.TensorSpec(
            shape=(None, AppConfig.MAX_LENGTH),
            dtype=tf.int32,
            name="input_ids",
        )
    ]

    tf2onnx.convert.from_keras(
        model=model,
        input_signature=input_signature,
        opset=AppConfig.ONNX_OPSET_VERSION,
        output_path=str(AppConfig.ONNX_MODEL_PATH),
    )

    print(f"Model exported to ONNX format at: {AppConfig.ONNX_MODEL_PATH}")


if __name__ == "__main__":
    convert_to_onnx()