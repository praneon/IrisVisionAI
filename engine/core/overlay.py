"""Overlay generation for segmentation visualization."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np



def generate_overlay(
    original_bgr: np.ndarray,
    mask: np.ndarray,
    class_colors: Dict[str, List[int]],
    alpha: float,
    output_path: str | Path,
) -> Path:
    """Blend class-colored mask on top of original image and write PNG."""
    overlay = np.zeros_like(original_bgr)

    for class_id, bgr in class_colors.items():
        overlay[mask == int(class_id)] = np.array(bgr, dtype=np.uint8)

    blended = cv2.addWeighted(original_bgr, 1.0 - alpha, overlay, alpha, 0.0)
    out = Path(output_path)
    cv2.imwrite(str(out), blended)
    return out
