from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from engine import run_analysis


def _canonical_manifest_hash(payload: dict) -> str:
    content = dict(payload)
    content.pop("manifest_sha256", None)
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_config(tmp_path: Path) -> dict:
    return {
        "output_dir": str(tmp_path / "out"),
        "model_config": {
            "model_version": "test_model",
            "device": "cpu",
            "overlay": {"alpha": 0.45, "class_colors_bgr": {"0": [0, 0, 0], "1": [0, 0, 255], "2": [0, 255, 0]}},
            "class_labels": {
                "background": 0,
                "pupil": 1,
                "iris": 2,
                "collarette": 3,
                "scurf_rim": 4,
                "contraction_furrows": 5,
            },
        },
        "extensions": {
            "micro_features": {"enabled": False, "version": "1"},
            "sector_mapping": {"enabled": False, "version": "1"},
            "interpretation": {"enabled": False, "version": "1"},
        },
    }


def _patch_fake_runtime(monkeypatch) -> None:
    class FakeSegmenter:
        def __init__(self, model_config):
            self.model_config = model_config

        def infer(self, gray):
            mask = np.full_like(gray, 2, dtype=np.uint8)
            mask[8:12, 8:12] = 1
            return mask

    def fake_measurements(mask):
        return {
            "pupil_pixels": int(np.sum(mask == 1)),
            "iris_pixels": int(np.sum(mask == 2)),
            "collarette_pixels": 0,
            "furrow_pixels": 0,
            "scurf_pixels": 0,
            "pupil_to_iris": 0.1,
            "collarette_to_iris": 0.0,
            "furrow_to_iris": 0.0,
            "scurf_to_iris": 0.0,
        }

    def fake_overlay(original_bgr, mask, class_colors, alpha, output_path):
        cv2.imwrite(str(output_path), original_bgr)

    monkeypatch.setattr(
        "engine.app.runtime._load_legacy_runtime_components",
        lambda: (FakeSegmenter, fake_measurements, fake_overlay),
    )


def test_run_analysis_contract(tmp_path: Path, monkeypatch) -> None:
    image = np.zeros((32, 32, 3), dtype=np.uint8)
    image[:, :, 1] = 120
    input_path = tmp_path / "sample.png"
    assert cv2.imwrite(str(input_path), image)

    _patch_fake_runtime(monkeypatch)
    config = _build_config(tmp_path)

    result = run_analysis(str(input_path), "cpu", config)
    payload = result.to_dict()

    assert payload["status"] == "success"
    assert payload["engine_version"]
    assert payload["model_version"] == "test_model"
    assert payload["input_filename"] == "sample.png"
    assert Path(payload["mask_path"]).exists()
    assert Path(payload["overlay_path"]).exists()
    assert Path(payload["results_json_path"]).exists()

    saved = json.loads(Path(payload["results_json_path"]).read_text(encoding="utf-8"))
    assert saved["status"] == "success"
    assert "metrics" in saved

    manifest_path = Path(config["output_dir"]) / "manifest.json"
    session_state_path = Path(config["output_dir"]) / "session_state.json"
    assert manifest_path.exists()
    assert session_state_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["run_state"] == "completed"
    assert manifest["engine_api_version"] == "1"
    assert manifest["manifest_schema_version"] == "1"
    assert manifest["manifest_sha256"] == _canonical_manifest_hash(manifest)

    session_state = json.loads(session_state_path.read_text(encoding="utf-8"))
    assert session_state["run_state"] == "completed"


def test_run_analysis_deterministic_results_payload(tmp_path: Path, monkeypatch) -> None:
    image = np.zeros((32, 32, 3), dtype=np.uint8)
    input_path = tmp_path / "sample.png"
    assert cv2.imwrite(str(input_path), image)

    _patch_fake_runtime(monkeypatch)
    config = _build_config(tmp_path)

    run_analysis(str(input_path), "cpu", config)
    result_path = Path(config["output_dir"]) / "results.json"
    first = json.loads(result_path.read_text(encoding="utf-8"))

    run_analysis(str(input_path), "cpu", config)
    second = json.loads(result_path.read_text(encoding="utf-8"))

    assert first == second
