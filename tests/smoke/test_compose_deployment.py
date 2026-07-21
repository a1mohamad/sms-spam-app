"""Black-box smoke test for the Docker Compose deployment."""

import json
import os
from typing import Any
from urllib.request import Request, urlopen
from uuid import UUID

import pytest


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def _request_json(
    request: Request,
    timeout_seconds: float = 10,
) -> tuple[int, Any, str]:
    """Send an HTTP request and decode its JSON response.

    Args:
        request: Configured HTTP request.
        timeout_seconds: Maximum time to wait for a response.

    Returns:
        Response status, decoded JSON payload, and request ID header.
    """
    with urlopen(request, timeout=timeout_seconds) as response:
        return (
            response.status,
            json.load(response),
            response.headers.get("X-Request-ID", ""),
        )


@pytest.mark.smoke
@pytest.mark.deployment
def test_compose_deployment_contract() -> None:
    """Verify readiness and prediction through the deployed API boundary."""
    base_url = os.getenv("DEPLOYMENT_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

    health_status, health_payload, health_request_id = _request_json(
        Request(f"{base_url}/health")
    )
    assert health_status == 200
    assert health_payload == {"status": "ok"}
    UUID(health_request_id)

    prediction_request = Request(
        f"{base_url}/predict",
        data=json.dumps(
            {
                "text": (
                    "Congratulations! You won a free prize. Claim it now!"
                )
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    prediction_status, prediction_payload, prediction_request_id = (
        _request_json(prediction_request)
    )

    assert prediction_status == 200
    assert prediction_payload["label"] in {"ham", "spam"}

    spam_probability = prediction_payload["spam_probability"]
    assert isinstance(spam_probability, (int, float))
    assert 0.0 <= spam_probability <= 1.0
    UUID(prediction_request_id)
