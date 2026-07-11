import pytest
from pydantic import ValidationError

from app.api.schemas import PredictRequest, PredictionResponse

def test_predict_request_non_empty_text():
    request = PredictRequest(text="Hello, this is a test message.")
    assert request.text == "Hello, this is a test message."


def test_predict_request_rejects_empty_text():
    with pytest.raises(ValidationError):
        PredictRequest(text="")


def test_prediction_response_rejects_invalid_label():
    with pytest.raises(ValidationError):
        PredictionResponse(
            label="unknown",
            spam_probability=0.5,
        )


def test_prediction_response_rejects_probability_above_one():
    with pytest.raises(ValidationError):
        PredictionResponse(
            label="spam",
            spam_probability=1.1,
        )


def test_prediction_reponse_accepts_valid_result():
    response = PredictionResponse(
        label="spam",
        spam_probability=0.92
    )

    assert response.label == "spam"
    assert response.spam_probability == 0.92