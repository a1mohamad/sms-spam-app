import importlib
import sys


def test_runtime_modules_do_not_import_tensorflow():
    importlib.import_module("app.core.config")
    importlib.import_module("app.ml.preprocessing")
    importlib.import_module("app.ml.predictor")

    # Runtime modules should stay lightweight; TensorFlow belongs in scripts only.
    assert "tensorflow" not in sys.modules
