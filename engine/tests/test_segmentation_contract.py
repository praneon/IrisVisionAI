import numpy as np
import pytest

from engine.core.segmentation import IrisSegmentationEngine


def _canonical_config() -> dict:
    return {
        "model_version": "test",
        "model_folder": "./models/test",
        "checkpoint_name": "checkpoint_final.pth",
        "folds": [0],
        "device": "cpu",
        "input_size": [8, 8],
        "tile_step_size": 0.5,
        "perform_everything_on_device": True,
        "class_labels": {
            "background": 0,
            "pupil": 1,
            "iris": 2,
            "collarette": 3,
            "scurf_rim": 4,
            "contraction_furrows": 5,
        },
    }


def test_class_map_mismatch_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _canonical_config()
    config["class_labels"] = {
        "background": 0,
        "pupil": 1,
        "iris": 2,
        "collarette": 3,
        "scurf_rim": 5,
        "contraction_furrows": 4,
    }

    def fail_if_called(self):  # pragma: no cover
        raise AssertionError("predictor load should not be called on class map mismatch")

    monkeypatch.setattr(IrisSegmentationEngine, "_load_predictor", fail_if_called)

    with pytest.raises(ValueError, match="class_labels must exactly match canonical"):
        IrisSegmentationEngine(config)


def test_predictor_initialized_once(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _canonical_config()
    load_count = {"count": 0}

    class FakePredictor:
        def predict_single_npy_array(self, **kwargs):
            return np.zeros((8, 8), dtype=np.uint8)

    def fake_load_predictor(self):
        load_count["count"] += 1
        return FakePredictor()

    monkeypatch.setattr(IrisSegmentationEngine, "_load_predictor", fake_load_predictor)

    engine = IrisSegmentationEngine(config)
    gray = np.zeros((8, 8), dtype=np.uint8)
    engine.infer(gray)
    engine.infer(gray)

    assert load_count["count"] == 1
