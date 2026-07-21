from unittest.mock import Mock
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.errors import (
    DatabaseUnavailableError,
    PersistenceError,
    PredictionError,
)


def test_prediction_failure_returns_safe_retryable_error(
    error_api_client: TestClient,
    mock_predictor: Mock,
) -> None:
    mock_predictor.predict.side_effect = PredictionError(
        "sensitive runtime details"
    )

    response = error_api_client.post("/predict", json={"text": "hello"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "prediction_unavailable"
    assert "sensitive" not in response.text
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_persistence_failure_returns_safe_retryable_error(
    error_api_client: TestClient,
    mock_save_prediction: Mock,
) -> None:
    mock_save_prediction.side_effect = PersistenceError(
        "postgresql://user:secret@database.internal/sms_spam"
    )

    response = error_api_client.post("/predict", json={"text": "hello"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "persistence_unavailable"
    assert "secret" not in response.text
    assert (
        response.json()["error"]["request_id"]
        == response.headers["x-request-id"]
    )


def test_unexpected_failure_returns_generic_error(
    error_api_client: TestClient,
    mock_predictor: Mock,
) -> None:
    mock_predictor.predict.side_effect = RuntimeError(
        "database password must not leak"
    )

    response = error_api_client.post("/predict", json={"text": "hello"})

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "password" not in response.text
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_successful_response_has_valid_request_id(api_client) -> None:
    response = api_client.get("/health")

    UUID(response.headers["x-request-id"])


def test_database_health_failure_returns_safe_retryable_error(
    error_api_client: TestClient,
    mock_database_health: Mock,
) -> None:
    """Verify readiness failures return a safe correlated response.

    Args:
        error_api_client: Test client configured to expose handled responses.
        mock_database_health: Database check configured to fail for the test.
    """
    mock_database_health.side_effect = DatabaseUnavailableError(
        "postgresql://user:secret@database.internal/sms_spam"
    )

    response = error_api_client.get("/health")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"
    assert "secret" not in response.text
    assert (
        response.json()["error"]["request_id"]
        == response.headers["x-request-id"]
    )
