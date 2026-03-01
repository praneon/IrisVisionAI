"""File and configuration utility helpers for IrisAtlasAI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def load_json(path: str | Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_dir(path: str | Path) -> Path:
    """Create an output directory if it does not exist."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def validate_image_extension(path: str | Path) -> None:
    """Validate that the input image extension is supported."""
    ext = Path(path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported input extension '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )
