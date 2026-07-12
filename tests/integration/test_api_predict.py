import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_app_serves_prediction_with_real_artifacts() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={"text": "Congratualtions you won a free prize"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["label"] in ("ham", "spam")
    assert isinstance(result["spam_probability"], float)
    assert 0.0 <= result["spam_probability"] <= 1.0