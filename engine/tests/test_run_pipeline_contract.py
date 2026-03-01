import argparse
import json
from pathlib import Path

import numpy as np
import pytest

import engine.app.run_pipeline as rp


def _write_model_config(path: Path, overlay_enabled: bool = False) -> None:
    model_config = {
        "model_version": "test_model_v0.5",
        "model_folder": "./models/nnunet_iris",
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
        "overlay": {
            "enabled": overlay_enabled,
            "alpha": 0.45,
            "class_colors_bgr": {
                "0": [0, 0, 0],
                "1": [255, 255, 0],
                "2": [0, 255, 0],
                "3": [255, 0, 255],
                "4": [0, 128, 255],
                "5": [0, 0, 255],
            },
        },
        "report": {"enabled": False},
    }
    path.write_text(json.dumps(model_config), encoding="utf-8")


def _args(input_path: Path, output_path: Path, config_dir: Path, pdf: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        input=str(input_path),
        output=str(output_path),
        config_dir=str(config_dir),
        pdf=pdf,
    )


def _prepare_common(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mask: np.ndarray,
) -> tuple[argparse.Namespace, Path]:
    input_path = tmp_path / "sample.png"
    input_path.write_bytes(b"fake")
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    _write_model_config(config_dir / "model_config.json", overlay_enabled=False)
    output_dir = tmp_path / "out"

    class FakeSegmenter:
        def __init__(self, model_config):
            self.model_config = model_config

        def infer(self, gray):
            return mask

    monkeypatch.setattr(rp, "IrisSegmentationEngine", FakeSegmenter)
    monkeypatch.setattr(
        rp,
        "load_nir_image",
        lambda p: (np.zeros((8, 8, 3), dtype=np.uint8), np.zeros((8, 8), dtype=np.uint8)),
    )
    return _args(input_path, output_dir, config_dir), output_dir


def test_json_keys_exact_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mask = np.full((8, 8), 2, dtype=np.uint8)
    args, output_dir = _prepare_common(tmp_path, monkeypatch, mask)

    result = rp.run(args)
    assert set(result.keys()) == {"status", "model_version", "input_filename", "segmentation", "ratios"}
    assert set(result["segmentation"].keys()) == {
        "pupil_pixels",
        "iris_pixels",
        "collarette_pixels",
        "furrow_pixels",
        "scurf_pixels",
    }
    assert set(result["ratios"].keys()) == {
        "pupil_to_iris",
        "collarette_to_iris",
        "furrow_to_iris",
        "scurf_to_iris",
    }
    assert "phenotype_labels" not in result

    payload = json.loads((output_dir / "sample_results.json").read_text(encoding="utf-8"))
    assert set(payload.keys()) == {"status", "model_version", "input_filename", "segmentation", "ratios"}


def test_mask_written_before_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mask = np.full((8, 8), 2, dtype=np.uint8)
    args, _ = _prepare_common(tmp_path, monkeypatch, mask)
    events: list[str] = []
    original_dump = json.dump

    def spy_imwrite(path, arr):
        events.append("mask")
        return True

    def spy_dump(obj, fp, **kwargs):
        events.append("json")
        return original_dump(obj, fp, **kwargs)

    monkeypatch.setattr(rp.cv2, "imwrite", spy_imwrite)
    monkeypatch.setattr(rp.json, "dump", spy_dump)

    rp.run(args)
    assert events[:2] == ["mask", "json"]


def test_mask_validation_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad_mask = np.full((8, 8), 9, dtype=np.uint8)
    args, _ = _prepare_common(tmp_path, monkeypatch, bad_mask)

    with pytest.raises(ValueError, match="Unexpected labels found"):
        rp.run(args)


def test_deterministic_result_with_mocked_segmentation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mask = np.full((8, 8), 2, dtype=np.uint8)
    args, output_dir = _prepare_common(tmp_path, monkeypatch, mask)

    result_1 = rp.run(args)
    json_1 = json.loads((output_dir / "sample_results.json").read_text(encoding="utf-8"))

    result_2 = rp.run(args)
    json_2 = json.loads((output_dir / "sample_results.json").read_text(encoding="utf-8"))

    assert result_1 == result_2
    assert json_1 == json_2
