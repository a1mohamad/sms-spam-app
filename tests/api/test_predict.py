from unittest.mock import Mock
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.config import AppConfig


def test_predict_returns_prediction_and_requests_persistence(
    api_client: TestClient,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
) -> None:
    text = (
        "Congratulations, you won a free prize! "
        "Call the number below: 12345678900"
    )

    response = api_client.post(
        "/predict",
        json={"text": text},
    )

    assert response.status_code == 200
    assert response.json() == {
        "label": "spam",
        "spam_probability": 0.9,
    }

    request_id = UUID(response.headers["x-request-id"])

    mock_predictor.predict.assert_called_once_with(text)
    mock_save_prediction.assert_called_once_with(
        request_id=request_id,
        message=text,
        label="spam",
        spam_probability=0.9,
        threshold=AppConfig.THRESHOLD,
    )


def test_predict_rejects_empty_text_before_processing(
    api_client: TestClient,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
) -> None:
    response = api_client.post(
        "/predict",
        json={"text": ""},
    )

    assert response.status_code == 422
    mock_predictor.predict.assert_not_called()
    mock_save_prediction.assert_not_called()


def test_predict_rejects_whitespace_only_text_before_processing(
    api_client: TestClient,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
) -> None:
    response = api_client.post(
        "/predict",
        json={"text": "     \n\t"},
    )

    assert response.status_code == 422
    mock_predictor.predict.assert_not_called()
    mock_save_prediction.assert_not_called()


def test_predict_rejects_message_above_character_limit(
    api_client: TestClient,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
) -> None:
    """Verify oversized SMS text is rejected before processing.

    Args:
        api_client: Isolated FastAPI test client.
        mock_predictor: Predictor double that must remain unused.
        mock_save_prediction: Persistence double that must remain unused.
    """
    response = api_client.post(
        "/predict",
        json={"text": "a" * (AppConfig.MAX_MESSAGE_LENGTH + 1)},
    )

    assert response.status_code == 422
    mock_predictor.predict.assert_not_called()
    mock_save_prediction.assert_not_called()


def test_predict_rejects_request_above_body_limit(
    api_client: TestClient,
    mock_predictor: Mock,
    mock_save_prediction: Mock,
) -> None:
    """Verify an oversized raw body is rejected before JSON parsing.

    Args:
        api_client: Isolated FastAPI test client.
        mock_predictor: Predictor double that must remain unused.
        mock_save_prediction: Persistence double that must remain unused.
    """
    response = api_client.post(
        "/predict",
        content=b"x" * (AppConfig.MAX_REQUEST_BODY_BYTES + 1),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"
    assert (
        response.json()["error"]["request_id"]
        == response.headers["x-request-id"]
    )
    mock_predictor.predict.assert_not_called()
    mock_save_prediction.assert_not_called()
