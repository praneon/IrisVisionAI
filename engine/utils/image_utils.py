"""Image loading helpers for NIR iris analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from .file_utils import validate_image_extension



def load_nir_image(path: str | Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load a NIR image and return both BGR and grayscale views.

    Returns:
        Tuple[np.ndarray, np.ndarray]: (bgr_image, gray_image)
    """
    validate_image_extension(path)
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to read image file: {path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray
