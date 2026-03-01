import numpy as np
import pytest

from engine.core.measurements import compute_measurements


def test_iris_pixels_zero_raises() -> None:
    mask = np.zeros((4, 4), dtype=np.uint8)
    with pytest.raises(ValueError, match="iris_pixels is zero"):
        compute_measurements(mask)
