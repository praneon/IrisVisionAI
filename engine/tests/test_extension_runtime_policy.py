from __future__ import annotations

import json
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from engine.app.analysis_types import ExtensionResult, ExtensionStatus
from engine.app.runtime import run_runtime


def _fake_components():
    class FakeSegmenter:
        def __init__(self, model_config):
            self.model_config = model_config

        def infer(self, gray):
            return np.full_like(gray, 2, dtype=np.uint8)

    def fake_measurements(mask):
        return {
            "pupil_pixels": 0,
            "iris_pixels": int(np.sum(mask == 2)),
            "collarette_pixels": 0,
            "furrow_pixels": 0,
            "scurf_pixels": 0,
            "pupil_to_iris": 0.0,
            "collarette_to_iris": 0.0,
            "furrow_to_iris": 0.0,
            "scurf_to_iris": 0.0,
        }

    def fake_overlay(original_bgr, mask, class_colors, alpha, output_path):
        cv2.imwrite(str(output_path), original_bgr)

    return FakeSegmenter, fake_measurements, fake_overlay


def _base_config(tmp_path: Path) -> dict:
    return {
        "output_dir": str(tmp_path / "out"),
        "model_config": {
            "model_version": "x",
            "overlay": {"alpha": 0.1, "class_colors_bgr": {"0": [0, 0, 0], "2": [0, 255, 0]}},
            "class_labels": {
                "background": 0,
                "pupil": 1,
                "iris": 2,
                "collarette": 3,
                "scurf_rim": 4,
                "contraction_furrows": 5,
            },
        },
    }


def test_extension_timeout_and_dependency_skip(tmp_path: Path, monkeypatch) -> None:
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    input_path = tmp_path / "in.png"
    assert cv2.imwrite(str(input_path), image)

    monkeypatch.setattr("engine.app.runtime._load_legacy_runtime_components", _fake_components)

    class SlowExtension:
        name = "micro_features"
        version = "1"
        requires = []
        optional_requires = []

        def run(self, context):
            time.sleep(0.2)
            return ExtensionResult(status=ExtensionStatus.SUCCESS, payload={"ok": True})

    class DependentExtension:
        name = "sector_mapping"
        version = "1"
        requires = ["micro_features"]
        optional_requires = []

        def run(self, context):
            return ExtensionResult(status=ExtensionStatus.SUCCESS, payload={"mapped": True})

    class PassExtension:
        name = "interpretation"
        version = "1"
        requires = []
        optional_requires = []

        def run(self, context):
            return ExtensionResult(status=ExtensionStatus.SUCCESS, payload={"text": "ok"})

    monkeypatch.setattr(
        "engine.app.runtime.build_extensions",
        lambda: {
            "micro_features": SlowExtension(),
            "sector_mapping": DependentExtension(),
            "interpretation": PassExtension(),
        },
    )

    config = _base_config(tmp_path)
    config["extensions"] = {
        "micro_features": {"enabled": True, "timeout_ms": 10, "version": "1"},
        "sector_mapping": {"enabled": True, "timeout_ms": 100, "version": "1"},
        "interpretation": {"enabled": True, "timeout_ms": 100, "version": "1"},
    }

    output = run_runtime(str(input_path), "cpu", config)
    telemetry = {entry.name: entry for entry in output.extension_telemetry}

    assert telemetry["micro_features"].status == ExtensionStatus.TIMEOUT
    assert telemetry["sector_mapping"].status == ExtensionStatus.SKIPPED
    assert telemetry["interpretation"].status == ExtensionStatus.SUCCESS


def test_run_state_failed_on_runtime_exception(tmp_path: Path, monkeypatch) -> None:
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    input_path = tmp_path / "in.png"
    assert cv2.imwrite(str(input_path), image)

    class BadSegmenter:
        def __init__(self, model_config):
            self.model_config = model_config

        def infer(self, gray):
            return np.full_like(gray, 9, dtype=np.uint8)

    def fake_measurements(mask):
        return {"iris_pixels": 0, "pupil_pixels": 0, "collarette_pixels": 0, "furrow_pixels": 0, "scurf_pixels": 0,
                "pupil_to_iris": 0.0, "collarette_to_iris": 0.0, "furrow_to_iris": 0.0, "scurf_to_iris": 0.0}

    def fake_overlay(original_bgr, mask, class_colors, alpha, output_path):
        cv2.imwrite(str(output_path), original_bgr)

    monkeypatch.setattr(
        "engine.app.runtime._load_legacy_runtime_components",
        lambda: (BadSegmenter, fake_measurements, fake_overlay),
    )

    config = _base_config(tmp_path)
    config["extensions"] = {
        "micro_features": {"enabled": False, "version": "1"},
        "sector_mapping": {"enabled": False, "version": "1"},
        "interpretation": {"enabled": False, "version": "1"},
    }

    with pytest.raises(ValueError, match="Unexpected labels"):
        run_runtime(str(input_path), "cpu", config)

    session_state = json.loads((Path(config["output_dir"]) / "session_state.json").read_text(encoding="utf-8"))
    assert session_state["run_state"] == "failed"
    assert "Unexpected labels" in str(session_state["error"])


def test_execution_order_lock() -> None:
    from engine.extensions.registry import EXECUTION_ORDER

    assert EXECUTION_ORDER == ["micro_features", "sector_mapping", "interpretation"]
