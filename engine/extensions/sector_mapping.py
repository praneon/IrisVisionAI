"""Sector mapping extension for iris clock-domain metrics."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from engine.app.analysis_types import ExtensionContext, ExtensionResult, ExtensionStatus


class SectorMappingExtension:
    """Map segmentation and micro-feature detections to clock sectors."""

    name = "sector_mapping"
    version = "1"
    requires: list[str] = []
    optional_requires: list[str] = ["micro_features"]

    def run(self, context: ExtensionContext) -> ExtensionResult:
        cfg = context.config.get("extensions", {}).get(self.name, {})
        if not bool(cfg.get("enabled", True)):
            return ExtensionResult(status=ExtensionStatus.SKIPPED, warning="Extension disabled by config.")

        sector_count = int(cfg.get("schema", 12))
        if sector_count not in {12, 24}:
            return ExtensionResult(
                status=ExtensionStatus.FAILED,
                warning=f"Unsupported sector schema '{sector_count}'. Expected 12 or 24.",
            )

        iris_mask = (context.segmentation_mask == 2).astype(np.uint8)
        if np.count_nonzero(iris_mask) == 0:
            return ExtensionResult(
                status=ExtensionStatus.SKIPPED,
                warning="Iris region missing; sector mapping skipped.",
            )

        center = self._estimate_center(iris_mask)
        if center is None:
            return ExtensionResult(
                status=ExtensionStatus.SKIPPED,
                warning="Unable to estimate iris center; sector mapping skipped.",
            )

        center_x, center_y, radius = center
        sector_metrics = self._compute_sector_metrics(
            mask=context.segmentation_mask,
            center_x=center_x,
            center_y=center_y,
            sector_count=sector_count,
            radius=radius,
            micro_boxes=context.extension_outputs.get("micro_features", {}).get("micro_feature_boxes", []),
        )

        heatmap_path = None
        if bool(cfg.get("generate_heatmap", False)):
            heatmap_path = self._build_heatmap(
                output_dir=context.output_dir,
                iris_mask=iris_mask,
                center_x=center_x,
                center_y=center_y,
                sector_count=sector_count,
            )

        payload: dict[str, Any] = {
            "sector_density_metrics": sector_metrics,
            "geometry": {
                "center_x": center_x,
                "center_y": center_y,
                "radius": radius,
                "sector_count": sector_count,
                "coordinate_system": {
                    "origin": "top_left",
                    "zero_angle": "12_oclock",
                    "direction": "clockwise",
                },
            },
            "sector_overlay_path": str(heatmap_path) if heatmap_path is not None else None,
        }
        return ExtensionResult(status=ExtensionStatus.SUCCESS, payload=payload)

    @staticmethod
    def _estimate_center(iris_mask: np.ndarray) -> tuple[float, float, float] | None:
        contours, _ = cv2.findContours(iris_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) <= 4.0:
            return None
        (cx, cy), radius = cv2.minEnclosingCircle(contour)
        return float(cx), float(cy), float(radius)

    @staticmethod
    def _sector_index(
        x: np.ndarray,
        y: np.ndarray,
        center_x: float,
        center_y: float,
        sector_count: int,
    ) -> np.ndarray:
        # float64 precision lock: round only at final bin assignment.
        dx = x.astype(np.float64) - np.float64(center_x)
        dy = np.float64(center_y) - y.astype(np.float64)
        angles = np.arctan2(dx, dy)
        angles = np.mod(angles, 2.0 * np.pi)
        return np.floor((angles / (2.0 * np.pi)) * sector_count).astype(np.int64)

    def _compute_sector_metrics(
        self,
        mask: np.ndarray,
        center_x: float,
        center_y: float,
        sector_count: int,
        radius: float,
        micro_boxes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        ys, xs = np.where(mask == 2)
        sector_idx = self._sector_index(xs, ys, center_x, center_y, sector_count)

        metrics: dict[str, Any] = {}
        for idx in range(sector_count):
            key = f"sector_{idx + 1}"
            metrics[key] = {
                "iris_pixels": 0,
                "collarette_pixels": 0,
                "scurf_rim_pixels": 0,
                "contraction_furrows_pixels": 0,
                "micro_feature_count": 0,
                "micro_feature_labels": {},
                "radius": radius,
            }

        for idx in range(sector_count):
            key = f"sector_{idx + 1}"
            mask_sector = sector_idx == idx
            if np.any(mask_sector):
                x_sector = xs[mask_sector]
                y_sector = ys[mask_sector]
                labels = mask[y_sector, x_sector]
                metrics[key]["iris_pixels"] = int(np.count_nonzero(labels == 2))
                metrics[key]["collarette_pixels"] = int(np.count_nonzero(labels == 3))
                metrics[key]["scurf_rim_pixels"] = int(np.count_nonzero(labels == 4))
                metrics[key]["contraction_furrows_pixels"] = int(np.count_nonzero(labels == 5))

        for box in micro_boxes:
            x1, y1, x2, y2 = box.get("bbox", [0, 0, 0, 0])
            cx = np.array([0.5 * (float(x1) + float(x2))], dtype=np.float64)
            cy = np.array([0.5 * (float(y1) + float(y2))], dtype=np.float64)
            idx = int(self._sector_index(cx, cy, center_x, center_y, sector_count)[0])
            key = f"sector_{idx + 1}"
            metrics[key]["micro_feature_count"] += 1
            label = str(box.get("label", "unknown"))
            label_counts = metrics[key]["micro_feature_labels"]
            label_counts[label] = int(label_counts.get(label, 0) + 1)

        return metrics

    def _build_heatmap(
        self,
        output_dir: Path,
        iris_mask: np.ndarray,
        center_x: float,
        center_y: float,
        sector_count: int,
    ) -> Path:
        ys, xs = np.where(iris_mask > 0)
        idx = self._sector_index(xs, ys, center_x, center_y, sector_count)
        normalized = np.zeros_like(iris_mask, dtype=np.uint8)
        normalized[ys, xs] = ((idx + 1) * int(255 / max(sector_count, 1))).astype(np.uint8)
        heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_TURBO)
        heatmap[iris_mask == 0] = 0

        out_path = output_dir / "sector_heatmap.png"
        cv2.imwrite(str(out_path), heatmap)
        return out_path
