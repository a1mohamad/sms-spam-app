import re
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from app.core.config import AppConfig
from app.utils.artifact_io import open_json_file


class Preprocessor:
    """Text preprocessor for the SMS spam classifier.

    Loads the vocabulary artifact used during model training and converts raw
    SMS text into fixed-length integer token IDs expected by the ONNX model.
    """

    def __init__(self, vocab_path: Path = AppConfig.VOCAB_PATH) -> None:
        """Load vocabulary and sequence-length metadata.

        Args:
            vocab_path: Path to the vocabulary configuration JSON artifact.
        """
        vocabs_artifact = open_json_file(vocab_path)

        self.vocabs: list[str] = vocabs_artifact["vocabs"]
        self.sequence_length: int = vocabs_artifact["output_sequence_length"]
        self.idx2word: dict[int, str] = dict(enumerate(self.vocabs))
        self.word2idx: dict[str, int] = {
            word: idx for idx, word in enumerate(self.vocabs)
        }
        self.unk_id: int = self.word2idx.get("UNK", 1)

    def standardize(self, text: str) -> str:
        """Normalize raw SMS text before tokenization.

        Args:
            text: Raw SMS message text.

        Returns:
            Lowercased text with punctuation removed.
        """
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def tokenize(self, text: str) -> NDArray[np.int32]:
        """Convert raw SMS text into fixed-length token IDs.

        Args:
            text: Raw SMS message text.

        Returns:
            Array with shape `(1, sequence_length)` and dtype `int32`.
        """
        text = self.standardize(text)
        tokens = text.split()
        ids = [
            self.word2idx.get(token, self.unk_id)
            for token in tokens
        ]

        # Match the model input shape by truncating long texts and padding short ones.
        ids = ids[:self.sequence_length]
        ids += [0] * (self.sequence_length - len(ids))

        return np.array([ids], dtype=np.int32)