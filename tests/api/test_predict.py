from unittest.mock import Mock

from fastapi.testclient import TestClient

def test_predict_return_prediction_contract(
    api_client: TestClient,
    mock_predictor: Mock,
) -> None:
    text = "Congratulations, you won a free prize! call the number below: 12345678900"

    response = api_client.post(
        "/predict",
        json={"text": text}
    )

    assert response.status_code == 200
    assert response.json() == {
        "label": "spam",
        "spam_probability": 0.9,
    }

    mock_predictor.predict.assert_called_once_with(text)

def test_predict_rejects_empty_text(api_client: TestClient) -> None:
    response = api_client.post(
        "/predict",
        json={"text": ""},
    )

    assert response.status_code == 422

def test_predict_rejects_whitespace_only_text(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/predict",
        json={"text": "     \n\t"},
    )

    assert response.status_code == 422