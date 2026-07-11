import numpy as np

from app.core.config import AppConfig
from app.ml.preprocessing import Preprocessor


def test_preprocessor_loads_real_vocab_artifact():
    preprocessor = Preprocessor(vocab_path=AppConfig.VOCAB_PATH)

    token_ids = preprocessor.tokenize("free prize claim now")

    assert token_ids.shape == (1, AppConfig.MAX_LENGTH)
    assert token_ids.dtype == np.int32