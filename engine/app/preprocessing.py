"""Input image loading and preprocessing helpers."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


SUPPORTED_IMAGE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


def load_image_for_analysis(input_path: str | Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load an image, always convert to grayscale, and emit non-blocking warnings."""

    path = Path(input_path)
    if not path.exists():
        raise ValueError(f"Input image does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input path must be a file: {path}")

    suffix = path.suffix.lower()
    if suffix and suffix not in SUPPORTED_IMAGE_SUFFIXES:
        # Extension check is advisory. OpenCV still attempts decode for unknown suffixes.
        warning = f"Input extension '{suffix}' is uncommon for this workflow; attempting decode."
    else:
        warning = ""

    image_bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError(f"Unable to decode image file: {path}")

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    warnings: list[str] = []
    if warning:
        warnings.append(warning)
    if likely_non_nir(image_bgr):
        warnings.append(
            "Input may not be a true NIR source (high inter-channel divergence detected). "
            "Analysis continues with grayscale conversion."
        )

    return image_bgr, gray, warnings


def likely_non_nir(image_bgr: np.ndarray) -> bool:
    """Heuristic check for non-NIR imagery.

    NIR captures are typically near-monochrome across channels. If channel divergence
    is high, we warn but do not fail.
    """

    image_f32 = image_bgr.astype(np.float32)
    channel_spread = np.mean(np.std(image_f32, axis=2))
    max_delta = float(np.max(np.abs(image_f32[:, :, 0] - image_f32[:, :, 2])))
    return bool(channel_spread > 12.0 or max_delta > 40.0)


def frozen_array_copy(array: np.ndarray) -> np.ndarray:
    """Create a read-only copy used for extension isolation."""

    out = np.array(array, copy=True)
    out.setflags(write=False)
    return out
