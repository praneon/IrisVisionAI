"""Core analysis runtime for IrisAtlas Engine."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import platform
import random
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np

from engine.app.analysis_types import (
    AnalysisResult,
    ExtensionContext,
    ExtensionResult,
    ExtensionStatus,
    ExtensionTelemetry,
    RunState,
)
from engine.app.preprocessing import frozen_array_copy, load_image_for_analysis
from engine.app.version import APP_VERSION, ENGINE_API_VERSION, ENGINE_VERSION, MANIFEST_SCHEMA_VERSION
from engine.extensions import EXECUTION_ORDER, build_extensions


CANONICAL_MASK_VALUES = {0, 1, 2, 3, 4, 5}


@dataclass
class RuntimeOutput:
    """Container for engine result and extension telemetry."""

    analysis_result: AnalysisResult
    extension_telemetry: list[ExtensionTelemetry]


def run_runtime(
    input_path: str | Path,
    device: str,
    config: dict[str, Any],
    stage_callback: Callable[[str, dict[str, Any]], None] | None = None,
) -> RuntimeOutput:
    """Run deterministic analysis and extension pipeline."""

    output_dir = Path(config.get("output_dir", Path.cwd() / "outputs")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file = Path(input_path).resolve()
    config_snapshot = _build_config_snapshot(config)
    state_path = _resolve_state_path(config, output_dir)

    _write_run_state(
        state_path=state_path,
        run_state=RunState.QUEUED,
        input_path=input_file,
        output_dir=output_dir,
        config_snapshot=config_snapshot,
        error=None,
    )
    _write_run_state(
        state_path=state_path,
        run_state=RunState.RUNNING,
        input_path=input_file,
        output_dir=output_dir,
        config_snapshot=config_snapshot,
        error=None,
    )

    try:
        original_bgr, gray, warnings = load_image_for_analysis(input_path)

        model_config = _load_model_config(config)
        model_config["device"] = _resolve_device(device)

        if stage_callback:
            stage_callback("segmentation_started", {"device": model_config["device"]})

        segmenter, compute_measurements, generate_overlay = _load_legacy_runtime_components()
        engine = segmenter(model_config)
        mask = _validate_mask_contract(engine.infer(gray))

        mask_path = output_dir / "mask.png"
        _require_write(mask_path, mask)

        input_copy_path = output_dir / "input.png"
        _require_write(input_copy_path, original_bgr)

        overlay_alpha = float(config.get("overlay_alpha", model_config.get("overlay", {}).get("alpha", 0.45)))
        overlay_path = output_dir / "overlay.png"
        generate_overlay(
            original_bgr=original_bgr,
            mask=mask,
            class_colors=model_config.get("overlay", {}).get("class_colors_bgr", {}),
            alpha=overlay_alpha,
            output_path=overlay_path,
        )

        metrics = compute_measurements(mask)
        results_json_path = output_dir / "results.json"

        extension_payloads: dict[str, dict[str, Any]] = {}
        extension_telemetry: list[ExtensionTelemetry] = []
        fail_on_extension_error = bool(config.get("fail_on_extension_error", False))
        if fail_on_extension_error:
            warnings.append("fail_on_extension_error=true is reserved in v0.5-alpha; soft-fail mode remains active.")

        extensions = build_extensions()
        extension_cfg = config.get("extensions", {})

        for extension_name in EXECUTION_ORDER:
            ext = extensions[extension_name]
            ext_settings = extension_cfg.get(extension_name, {})
            timeout_ms = int(ext_settings.get("timeout_ms", 30000))

            dependency_status = _validate_dependencies(extension_name, ext, extension_payloads)
            if dependency_status is not None:
                status, warning = dependency_status
                telemetry = ExtensionTelemetry(
                    name=extension_name,
                    version=str(getattr(ext, "version", "1")),
                    status=status,
                    duration_ms=0,
                    peak_memory_mb=None,
                    warning=warning,
                )
                extension_telemetry.append(telemetry)
                warnings.append(f"[{extension_name}] {warning}")
                continue

            cfg_version = str(ext_settings.get("version", getattr(ext, "version", "1")))
            impl_version = str(getattr(ext, "version", "1"))
            if cfg_version != impl_version:
                warnings.append(
                    f"[{extension_name}] Config version {cfg_version} differs from implementation {impl_version}; "
                    "executing implementation version."
                )

            context = ExtensionContext(
                input_path=input_file,
                output_dir=output_dir,
                grayscale_image=frozen_array_copy(gray),
                original_bgr=frozen_array_copy(original_bgr),
                segmentation_mask=frozen_array_copy(mask),
                iris_mask=frozen_array_copy((mask == 2).astype(np.uint8)),
                metrics=dict(metrics),
                device=model_config["device"],
                model_version=str(model_config.get("model_version", "unknown")),
                config=_deepcopy_jsonable(config_snapshot),
                extension_outputs=_deepcopy_jsonable(extension_payloads),
            )

            if stage_callback:
                stage_callback(f"{extension_name}_started", {"timeout_ms": timeout_ms})

            _set_deterministic_seeds()
            start = time.perf_counter()
            tracemalloc.start()
            try:
                ext_result = _run_with_timeout(ext.run, context, timeout_ms=timeout_ms)
            except TimeoutError:
                duration_ms = int((time.perf_counter() - start) * 1000)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                warning = f"Extension timed out after {timeout_ms} ms"
                warnings.append(f"[{extension_name}] {warning}")
                telemetry = ExtensionTelemetry(
                    name=extension_name,
                    version=impl_version,
                    status=ExtensionStatus.TIMEOUT,
                    duration_ms=duration_ms,
                    peak_memory_mb=round(peak / (1024 * 1024), 3),
                    warning=warning,
                )
                extension_telemetry.append(telemetry)
                if stage_callback:
                    stage_callback(f"{extension_name}_done", {"status": ExtensionStatus.TIMEOUT.value})
                continue
            except Exception as exc:  # pragma: no cover - runtime protection
                duration_ms = int((time.perf_counter() - start) * 1000)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                warning = f"Extension error: {exc}"
                warnings.append(f"[{extension_name}] {warning}")
                telemetry = ExtensionTelemetry(
                    name=extension_name,
                    version=impl_version,
                    status=ExtensionStatus.FAILED,
                    duration_ms=duration_ms,
                    peak_memory_mb=round(peak / (1024 * 1024), 3),
                    warning=warning,
                )
                extension_telemetry.append(telemetry)
                if stage_callback:
                    stage_callback(f"{extension_name}_done", {"status": ExtensionStatus.FAILED.value})
                continue

            duration_ms = int((time.perf_counter() - start) * 1000)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            if not isinstance(ext_result, ExtensionResult):
                ext_result = ExtensionResult(
                    status=ExtensionStatus.FAILED,
                    warning=f"Invalid extension result type from {extension_name}",
                )

            if ext_result.warning:
                warnings.append(f"[{extension_name}] {ext_result.warning}")

            if ext_result.status == ExtensionStatus.SUCCESS:
                extension_payloads[extension_name] = _deepcopy_jsonable(ext_result.payload)

            telemetry = ExtensionTelemetry(
                name=extension_name,
                version=impl_version,
                status=ext_result.status,
                duration_ms=duration_ms,
                peak_memory_mb=round(peak / (1024 * 1024), 3),
                model_version=ext_result.model_version,
                warning=ext_result.warning,
            )
            extension_telemetry.append(telemetry)

            if stage_callback:
                stage_callback(f"{extension_name}_done", {"status": ext_result.status.value})

        analysis_result = AnalysisResult(
            status="success",
            engine_version=ENGINE_VERSION,
            model_version=str(model_config.get("model_version", "unknown")),
            input_filename=input_file.name,
            device=str(model_config.get("device", "cpu")),
            mask_path=str(mask_path),
            overlay_path=str(overlay_path),
            results_json_path=str(results_json_path),
            metrics={key: _normalize_metric_value(value) for key, value in metrics.items()},
            warnings=warnings,
            extensions=extension_payloads,
        )

        payload = analysis_result.to_dict()
        # Optional mirrored fields for UI convenience.
        for extension_name, ext_data in extension_payloads.items():
            if extension_name == "micro_features":
                payload["micro_feature_metrics"] = ext_data.get("micro_feature_metrics")
                payload["micro_feature_boxes"] = ext_data.get("micro_feature_boxes")
            if extension_name == "sector_mapping":
                payload["sector_density_metrics"] = ext_data.get("sector_density_metrics")
            if extension_name == "interpretation":
                payload["interpretation_summary"] = ext_data.get("interpretation_summary")
                payload["interpretation_text"] = ext_data.get("interpretation_text")

        _atomic_write_json(results_json_path, payload)

        manifest_path = output_dir / "manifest.json"
        manifest = _build_manifest_payload(
            analysis_result=analysis_result,
            extension_telemetry=extension_telemetry,
            config_snapshot=config_snapshot,
            model_config=model_config,
            run_state=RunState.COMPLETED,
            input_path=input_file,
            output_dir=output_dir,
            timestamp_override=config.get("manifest_timestamp"),
        )
        _atomic_write_json(manifest_path, manifest)

        _write_run_state(
            state_path=state_path,
            run_state=RunState.COMPLETED,
            input_path=input_file,
            output_dir=output_dir,
            config_snapshot=config_snapshot,
            error=None,
        )

        if stage_callback:
            stage_callback("analysis_done", {"result": "success"})
        return RuntimeOutput(analysis_result=analysis_result, extension_telemetry=extension_telemetry)

    except Exception as exc:
        _write_run_state(
            state_path=state_path,
            run_state=RunState.FAILED,
            input_path=input_file,
            output_dir=output_dir,
            config_snapshot=config_snapshot,
            error=str(exc),
        )
        if stage_callback:
            stage_callback("analysis_done", {"result": "failed", "error": str(exc)})
        raise


def _run_with_timeout(fn: Callable[[ExtensionContext], ExtensionResult], context: ExtensionContext, timeout_ms: int) -> ExtensionResult:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, context)
        return future.result(timeout=max(timeout_ms, 1) / 1000.0)


def _load_legacy_runtime_components():
    """Load core runtime components from the unified engine package.

    Kept with the existing name to preserve test monkeypatch compatibility.
    """

    from engine.core.measurements import compute_measurements
    from engine.core.overlay import generate_overlay
    from engine.core.segmentation import IrisSegmentationEngine

    return IrisSegmentationEngine, compute_measurements, generate_overlay


def _validate_mask_contract(mask: np.ndarray) -> np.ndarray:
    mask_uint8 = np.asarray(mask, dtype=np.uint8)
    if mask_uint8.ndim != 2:
        raise ValueError("Segmentation mask must be single-channel")
    if not set(np.unique(mask_uint8)).issubset(CANONICAL_MASK_VALUES):
        raise ValueError("Unexpected labels found in segmentation output")
    return mask_uint8


def _require_write(path: Path, image: np.ndarray) -> None:
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"Failed to write image: {path}")


def _resolve_device(device: str) -> str:
    device_normalized = str(device or "auto").strip().lower()
    if device_normalized in {"cpu", "cuda"}:
        return device_normalized
    if device_normalized != "auto":
        return "cpu"

    try:
        import torch  # type: ignore[import-not-found]

        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


def _load_model_config(config: dict[str, Any]) -> dict[str, Any]:
    inline = config.get("model_config")
    if isinstance(inline, dict):
        return _deepcopy_jsonable(inline)

    path_raw = str(config.get("model_config_path", "")).strip()
    if not path_raw:
        path = Path(__file__).resolve().parent.parent / "configs" / "model_config.json"
    else:
        path = Path(path_raw).expanduser().resolve()

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if config.get("model_folder"):
        payload["model_folder"] = str(config["model_folder"])

    return payload


def _normalize_metric_value(value: float | int) -> float | int:
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    return value


def _set_deterministic_seeds() -> None:
    random.seed(0)
    np.random.seed(0)
    try:
        import torch  # type: ignore[import-not-found]

        torch.manual_seed(0)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(0)
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        return


def _validate_dependencies(extension_name: str, extension: object, outputs: dict[str, dict[str, Any]]) -> tuple[ExtensionStatus, str] | None:
    requires = list(getattr(extension, "requires", []))
    for dep in requires:
        if dep not in outputs:
            return ExtensionStatus.SKIPPED, f"Required dependency '{dep}' not available for {extension_name}."
    return None


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)


def _deepcopy_jsonable(payload: Any) -> Any:
    return json.loads(json.dumps(payload))


def _build_config_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    # Exclude ephemeral/private runtime keys from reproducibility snapshots.
    payload = {key: value for key, value in config.items() if not str(key).startswith("_")}
    return _deepcopy_jsonable(payload)


def _resolve_state_path(config: dict[str, Any], output_dir: Path) -> Path:
    state_raw = str(config.get("state_path", "")).strip()
    if state_raw:
        return Path(state_raw).expanduser().resolve()
    return output_dir / "session_state.json"


def _write_run_state(
    state_path: Path,
    run_state: RunState,
    input_path: Path,
    output_dir: Path,
    config_snapshot: dict[str, Any],
    error: str | None,
) -> None:
    payload = {
        "run_state": run_state.value,
        "timestamp": _utc_now_iso(),
        "input_path": str(input_path),
        "output_dir": str(output_dir),
        "config_snapshot": config_snapshot,
        "error": error,
    }
    _atomic_write_json(state_path, payload)


def _build_manifest_payload(
    analysis_result: AnalysisResult,
    extension_telemetry: list[ExtensionTelemetry],
    config_snapshot: dict[str, Any],
    model_config: dict[str, Any],
    run_state: RunState,
    input_path: Path,
    output_dir: Path,
    timestamp_override: Any | None,
) -> dict[str, Any]:
    timestamp = str(timestamp_override).strip() if timestamp_override is not None else ""
    if not timestamp:
        timestamp = _utc_now_iso()

    model_version = str(model_config.get("model_version") or analysis_result.model_version or "unknown")
    model_hash = _compute_model_hash(model_config=model_config, config_snapshot=config_snapshot)

    payload: dict[str, Any] = {
        "app_version": APP_VERSION,
        "engine_version": ENGINE_VERSION,
        "engine_api_version": ENGINE_API_VERSION,
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "model_version": model_version,
        "device": analysis_result.device,
        "timestamp": timestamp,
        "model_hash": model_hash,
        "config_snapshot": config_snapshot,
        "environment_snapshot": _build_environment_snapshot(),
        "extensions": [entry.to_manifest() for entry in extension_telemetry],
        "run_state": run_state.value,
        "input_path": str(input_path),
        "output_dir": str(output_dir),
        "artifacts": {
            "mask_path": analysis_result.mask_path,
            "overlay_path": analysis_result.overlay_path,
            "results_json_path": analysis_result.results_json_path,
        },
    }

    payload["manifest_sha256"] = _canonical_payload_sha256(payload)
    return payload


def _build_environment_snapshot() -> dict[str, Any]:
    packages = {
        "numpy": _safe_package_version("numpy"),
        "opencv-python": _safe_package_version("opencv-python"),
        "torch": _safe_package_version("torch"),
        "PySide6": _safe_package_version("PySide6"),
        "ultralytics": _safe_package_version("ultralytics"),
    }

    cuda_version = None
    try:
        import torch  # type: ignore[import-not-found]

        cuda_version = getattr(getattr(torch, "version", None), "cuda", None)
    except Exception:
        cuda_version = None

    return {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "cuda_version": cuda_version,
        "packages": packages,
    }


def _safe_package_version(name: str) -> str | None:
    try:
        return importlib_metadata.version(name)
    except importlib_metadata.PackageNotFoundError:
        return None
    except Exception:
        return None


def _compute_model_hash(model_config: dict[str, Any], config_snapshot: dict[str, Any]) -> str:
    explicit_hash = config_snapshot.get("model_hash") or model_config.get("model_hash")
    if explicit_hash:
        return str(explicit_hash)

    model_folder = str(model_config.get("model_folder", "")).strip()
    checkpoint_name = str(model_config.get("checkpoint_name", "")).strip()
    if model_folder and checkpoint_name:
        checkpoint_path = Path(model_folder).expanduser().resolve() / checkpoint_name
        if checkpoint_path.exists() and checkpoint_path.is_file():
            return _sha256_file(checkpoint_path)

    return _canonical_payload_sha256(model_config)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_payload_sha256(payload: dict[str, Any]) -> str:
    content = dict(payload)
    content.pop("manifest_sha256", None)
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
