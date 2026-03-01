"""Public API for IrisAtlas Engine desktop runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.app.analysis_types import AnalysisResult, ExtensionTelemetry
from engine.app.runtime import run_runtime


def run_analysis(input_path: str | Path, device: str, config: dict[str, Any]) -> AnalysisResult:
    """Run full analysis pipeline and return a typed result object.

    Parameters
    ----------
    input_path:
        Path to input image.
    device:
        One of ``auto``, ``cpu``, or ``cuda``.
    config:
        Runtime configuration dictionary.
    """

    runtime_output = run_runtime(input_path=input_path, device=device, config=config)
    # Keep extension telemetry available for callers that need manifest assembly.
    config["_extension_telemetry"] = [entry.to_manifest() for entry in runtime_output.extension_telemetry]
    return runtime_output.analysis_result


def get_last_extension_telemetry(config: dict[str, Any]) -> list[ExtensionTelemetry] | list[dict[str, Any]]:
    """Return extension telemetry captured during the latest ``run_analysis`` call."""

    return list(config.get("_extension_telemetry", []))
