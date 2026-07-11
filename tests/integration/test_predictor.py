from app.ml.predictor import SpamPredictor


def assert_valid_prediction(result: dict[str, str | float]) -> None:
    assert set(result) == {"label", "spam_probability"}
    assert result["label"] in {"ham", "spam"}
    assert isinstance(result["spam_probability"], float)
    assert 0.0 <= result["spam_probability"] <= 1.0


def test_predictor_initializes_with_runtime_artifacts():
    predictor = SpamPredictor()

    assert predictor.input_name
    assert predictor.label_mapping == {
        "0": "ham",
        "1": "spam",
    }


def test_predictor_returns_stable_prediction_contract():
    predictor = SpamPredictor()

    result = predictor.predict("Congratulations you won a free prize")

    assert_valid_prediction(result)


def test_predictor_handles_ham_like_text():
    predictor = SpamPredictor()

    result = predictor.predict("Hey are we still meeting today")

    assert_valid_prediction(result)


def test_predictor_handles_spam_like_text():
    predictor = SpamPredictor()

    result = predictor.predict("URGENT you won a free cash prize claim now")

    assert_valid_prediction(result)


def test_predictor_handles_empty_text():
    predictor = SpamPredictor()

    result = predictor.predict("")

    assert_valid_prediction(result)


def test_predictor_handles_long_text():
    predictor = SpamPredictor()
    long_text = "free prize now " * 500

    result = predictor.predict(long_text)

    assert_valid_prediction(result)


def test_predictor_is_deterministic_for_same_input():
    predictor = SpamPredictor()
    text = "Congratulations you won a free prize"

    first_result = predictor.predict(text)
    second_result = predictor.predict(text)

    assert first_result == second_result
