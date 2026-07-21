"""Process-level smoke test for the deployable API runtime."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
from uuid import UUID

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_available_port() -> int:
    """Ask the operating system for an available local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("127.0.0.1", 0))
        return int(server_socket.getsockname()[1])


@pytest.mark.smoke
@pytest.mark.database
def test_runtime_process_starts_and_reports_healthy() -> None:
    """Start Uvicorn as a real process and verify its health contract."""
    port = _find_available_port()
    health_url = f"http://127.0.0.1:{port}/health"
    environment = os.environ.copy()

    # Preserve any existing import path while ensuring the project is importable.
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        path
        for path in (str(PROJECT_ROOT), existing_pythonpath)
        if path
    )

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
            "--no-access-log",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        deadline = time.monotonic() + 20

        while time.monotonic() < deadline:
            if process.poll() is not None:
                output, _ = process.communicate()
                pytest.fail(
                    "API process exited before becoming healthy.\n"
                    f"{output}"
                )

            try:
                with urlopen(health_url, timeout=1) as response:
                    payload = json.load(response)

                assert response.status == 200
                assert payload == {"status": "ok"}
                UUID(response.headers["X-Request-ID"])
                break
            except (TimeoutError, URLError):
                time.sleep(0.1)
        else:
            pytest.fail("API process did not become healthy within 20 seconds.")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)
