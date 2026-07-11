from app.ml.predictor import SpamPredictor


def make_predictor_for_label_tests(threshold: float = 0.5) -> SpamPredictor:
    predictor = SpamPredictor.__new__(SpamPredictor)
    predictor.threshold = threshold
    predictor.label_mapping = {
        "0": "ham",
        "1": "spam",
    }
    return predictor


def test_label_from_probability_returns_spam_at_threshold():
    predictor = make_predictor_for_label_tests(threshold=0.5)

    assert predictor.label_from_probability(0.5) == "spam"


def test_label_from_probability_returns_ham_below_threshold():
    predictor = make_predictor_for_label_tests(threshold=0.5)

    assert predictor.label_from_probability(0.49) == "ham"


def test_label_from_probability_uses_custom_threshold():
    predictor = make_predictor_for_label_tests(threshold=0.8)

    assert predictor.label_from_probability(0.79) == "ham"
    assert predictor.label_from_probability(0.8) == "spam"
