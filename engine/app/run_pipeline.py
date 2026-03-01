"""CLI pipeline for IrisAtlasAI structural iris analysis.

This module is retained for deterministic single-image CLI runs. The desktop API
uses ``engine.run_analysis``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np

from engine.core.measurements import compute_measurements
from engine.core.overlay import generate_overlay
from engine.core.segmentation import IrisSegmentationEngine
from engine.utils.file_utils import ensure_dir, load_json
from engine.utils.image_utils import load_nir_image


CANONICAL_MASK_VALUES = {0, 1, 2, 3, 4, 5}


def _validate_single_image_input(input_path: Path) -> None:
    if not input_path.exists():
        raise ValueError(f"Input image does not exist: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input must be a single image file, got: {input_path}")


def _validate_mask_contract(mask: np.ndarray) -> np.ndarray:
    mask_uint8 = np.asarray(mask, dtype=np.uint8)
    if mask_uint8.ndim != 2:
        raise ValueError("Segmentation mask must be single-channel")
    if not set(np.unique(mask_uint8)).issubset(CANONICAL_MASK_VALUES):
        raise ValueError("Unexpected labels found in segmentation output")
    return mask_uint8


def build_result(
    input_filename: str,
    model_version: str,
    measurements: Dict[str, float | int],
) -> Dict[str, Any]:
    """Build output JSON exactly matching required schema."""
    return {
        "status": "success",
        "model_version": str(model_version),
        "input_filename": input_filename,
        "segmentation": {
            "pupil_pixels": int(measurements["pupil_pixels"]),
            "iris_pixels": int(measurements["iris_pixels"]),
            "collarette_pixels": int(measurements["collarette_pixels"]),
            "furrow_pixels": int(measurements["furrow_pixels"]),
            "scurf_pixels": int(measurements["scurf_pixels"]),
        },
        "ratios": {
            "pupil_to_iris": float(measurements["pupil_to_iris"]),
            "collarette_to_iris": float(measurements["collarette_to_iris"]),
            "furrow_to_iris": float(measurements["furrow_to_iris"]),
            "scurf_to_iris": float(measurements["scurf_to_iris"]),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IrisAtlasAI NIR structural analysis pipeline")
    parser.add_argument("--input", required=True, help="Path to NIR iris image (.png/.jpg)")
    parser.add_argument("--output", required=True, help="Output folder path")
    parser.add_argument(
        "--config-dir",
        default=str(Path(__file__).parent.parent / "configs"),
        help="Directory containing model_config.json",
    )
    parser.add_argument("--pdf", action="store_true", help="Generate optional PDF report")
    return parser.parse_args()


def run(args: argparse.Namespace) -> Dict[str, Any]:
    config_dir = Path(args.config_dir)
    input_path = Path(args.input)
    _validate_single_image_input(input_path)

    model_config = load_json(config_dir / "model_config.json")
    output_dir = ensure_dir(args.output)
    original_bgr, gray = load_nir_image(input_path)

    segmenter = IrisSegmentationEngine(model_config)
    mask = _validate_mask_contract(segmenter.infer(gray))

    mask_path = output_dir / f"{input_path.stem}_mask.png"
    if not cv2.imwrite(str(mask_path), mask):
        raise ValueError(f"Failed to write segmentation mask: {mask_path}")

    measurements = compute_measurements(mask)
    result = build_result(
        input_filename=input_path.name,
        model_version=str(model_config.get("model_version", "unknown")),
        measurements=measurements,
    )

    json_path = output_dir / f"{input_path.stem}_results.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    overlay_enabled = bool(model_config.get("overlay", {}).get("enabled", True))
    overlay_path = output_dir / f"{input_path.stem}_overlay.png"
    if overlay_enabled:
        generate_overlay(
            original_bgr=original_bgr,
            mask=mask,
            class_colors=model_config["overlay"]["class_colors_bgr"],
            alpha=float(model_config["overlay"]["alpha"]),
            output_path=overlay_path,
        )

    pdf_enabled = args.pdf or bool(model_config.get("report", {}).get("enabled", False))
    if pdf_enabled:
        from engine.core.report import create_pdf_report

        if not overlay_enabled:
            generate_overlay(
                original_bgr=original_bgr,
                mask=mask,
                class_colors=model_config["overlay"]["class_colors_bgr"],
                alpha=float(model_config["overlay"]["alpha"]),
                output_path=overlay_path,
            )
        pdf_path = output_dir / f"{input_path.stem}_report.pdf"
        create_pdf_report(input_path, overlay_path, pdf_path, result)

    return result


def main() -> None:
    result = run(parse_args())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
