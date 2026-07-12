from fastapi.testclient import TestClient


def test_health_check_returns_ok_status(
    api_client: TestClient,
) -> None:
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}