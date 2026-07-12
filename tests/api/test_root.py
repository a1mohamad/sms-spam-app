from fastapi.testclient import TestClient

def test_root_returns_api_metadata(api_client: TestClient) -> None:
    response = api_client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "SMS Spam Classifier",
        "version": "1.0.0",
        "docs": "/docs",
    }