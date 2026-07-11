import json
from pathlib import Path
from typing import Any


def open_json_file(path: Path) -> dict[str, Any]:
    """Load and return a JSON object from disk."""
    with open(path, "r", encoding="utf-8") as f:
        artifact_file = json.load(f)

    return artifact_file