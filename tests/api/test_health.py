from unittest.mock import Mock

from fastapi.testclient import TestClient


def test_health_check_returns_ok_status(
    api_client: TestClient,
    mock_database_health: Mock,
) -> None:
    """Verify health reports ready only after checking the database.

    Args:
        api_client: Isolated FastAPI test client.
        mock_database_health: Observable database readiness check.
    """
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_database_health.assert_called_once_with()
