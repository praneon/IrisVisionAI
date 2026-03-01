"""Typed contracts for IrisAtlas engine runtime and extensions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import numpy as np


class ExtensionStatus(str, Enum):
    """Allowed extension execution states."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    FAILED = "failed"


class RunState(str, Enum):
    """Allowed run lifecycle states."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ExtensionTelemetry:
    """Audit metadata for each extension stage."""

    name: str
    version: str
    status: ExtensionStatus
    duration_ms: int
    peak_memory_mb: float | None
    model_version: str | None = None
    warning: str | None = None

    def to_manifest(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class ExtensionResult:
    """Structured output returned by extensions."""

    status: ExtensionStatus
    payload: dict[str, Any] = field(default_factory=dict)
    warning: str | None = None
    model_version: str | None = None


@dataclass(frozen=True)
class ExtensionContext:
    """Read-only runtime snapshot provided to each extension."""

    input_path: Path
    output_dir: Path
    grayscale_image: np.ndarray
    original_bgr: np.ndarray
    segmentation_mask: np.ndarray
    iris_mask: np.ndarray
    metrics: dict[str, float | int]
    device: str
    model_version: str
    config: dict[str, Any]
    extension_outputs: dict[str, dict[str, Any]]


class ExtensionSpec(Protocol):
    """Protocol every extension implementation must satisfy."""

    name: str
    version: str
    requires: list[str]
    optional_requires: list[str]

    def run(self, context: ExtensionContext) -> ExtensionResult:
        """Execute extension using a read-only context snapshot."""


@dataclass
class AnalysisResult:
    """Result object returned by ``engine.run_analysis``."""

    status: str
    engine_version: str
    model_version: str
    input_filename: str
    device: str
    mask_path: str
    overlay_path: str
    results_json_path: str
    metrics: dict[str, float | int]
    warnings: list[str]
    extensions: dict[str, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "engine_version": self.engine_version,
            "model_version": self.model_version,
            "input_filename": self.input_filename,
            "device": self.device,
            "mask_path": self.mask_path,
            "overlay_path": self.overlay_path,
            "results_json_path": self.results_json_path,
            "metrics": self.metrics,
            "warnings": list(self.warnings),
            "extensions": self.extensions,
        }
