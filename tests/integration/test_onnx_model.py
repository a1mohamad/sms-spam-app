import onnx
import onnxruntime as ort

from app.core.config import AppConfig
from app.ml.preprocessing import Preprocessor


def test_onnx_model_file_is_valid():
    model = onnx.load(AppConfig.ONNX_MODEL_PATH)

    onnx.checker.check_model(model)


def test_onnx_model_runs_with_preprocessor_output():
    session = ort.InferenceSession(str(AppConfig.ONNX_MODEL_PATH))
    input_name = session.get_inputs()[0].name

    preprocessor = Preprocessor(vocab_path=AppConfig.VOCAB_PATH)
    token_ids = preprocessor.tokenize("Congratulations you won a free prize")

    outputs = session.run(None, {input_name: token_ids})

    assert len(outputs) > 0
    assert outputs[0].shape[0] == 1