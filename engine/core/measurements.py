"""Measurement calculations from segmentation masks."""

from __future__ import annotations

from typing import Dict

import numpy as np


CLASS_IDS = {
    "pupil": 1,
    "iris": 2,
    "collarette": 3,
    "furrow": 4,
    "scurf": 5,
}



def compute_measurements(mask: np.ndarray) -> Dict[str, float | int]:
    """Compute deterministic pixel counts and structural ratios."""
    pupil_pixels = int(np.sum(mask == CLASS_IDS["pupil"]))
    iris_pixels = int(np.sum(mask == CLASS_IDS["iris"]))
    collarette_pixels = int(np.sum(mask == CLASS_IDS["collarette"]))
    furrow_pixels = int(np.sum(mask == CLASS_IDS["furrow"]))
    scurf_pixels = int(np.sum(mask == CLASS_IDS["scurf"]))

    if iris_pixels <= 0:
        raise ValueError("iris_pixels is zero; cannot compute ratios")

    return {
        "pupil_pixels": pupil_pixels,
        "iris_pixels": iris_pixels,
        "collarette_pixels": collarette_pixels,
        "furrow_pixels": furrow_pixels,
        "scurf_pixels": scurf_pixels,
        "pupil_to_iris": float(pupil_pixels / iris_pixels),
        "collarette_to_iris": float(collarette_pixels / iris_pixels),
        "furrow_to_iris": float(furrow_pixels / iris_pixels),
        "scurf_to_iris": float(scurf_pixels / iris_pixels),
    }
