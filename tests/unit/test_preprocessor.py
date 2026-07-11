import numpy as np


def test_standardize_lowercases_and_removes_punctuation(preprocessor):
    text = preprocessor.standardize("FREE!!! Prize, NOW.")

    assert text == "free prize now"


def test_tokenize_returns_expected_shape(preprocessor):
    token_ids = preprocessor.tokenize("free prize claim now")

    assert token_ids.shape == (1, 100)


def test_tokenize_returns_int32(preprocessor):
    token_ids = preprocessor.tokenize("free prize claim now")

    assert token_ids.dtype == np.int32


def test_tokenize_pads_short_text(preprocessor):
    token_ids = preprocessor.tokenize("hello")

    assert token_ids[0, 0] == preprocessor.word2idx["hello"]
    assert np.all(token_ids[0, 1:] == 0)


def test_tokenize_truncates_long_text(preprocessor):
    long_text = "hello " * 300

    token_ids = preprocessor.tokenize(long_text)

    assert token_ids.shape == (1, 100)


def test_unknown_word_maps_to_unk_id(preprocessor):
    token_ids = preprocessor.tokenize("zzzzunknownword")

    assert token_ids[0, 0] == preprocessor.unk_id


def test_tokenize_empty_text_returns_only_padding(preprocessor):
    token_ids = preprocessor.tokenize("")

    assert token_ids.shape == (1, 100)
    assert (token_ids == 0).all()


def test_tokenize_whitespace_only_text_returns_only_padding(preprocessor):
    token_ids = preprocessor.tokenize("     \n\t   ")

    assert token_ids.shape == (1, 100)
    assert (token_ids == 0).all()


def test_tokenize_maps_known_words_to_correct_ids(preprocessor):
    token_ids = preprocessor.tokenize("free prize now")

    assert token_ids[0, 0] == preprocessor.word2idx["free"]
    assert token_ids[0, 1] == preprocessor.word2idx["prize"]
    assert token_ids[0, 2] == preprocessor.word2idx["now"]