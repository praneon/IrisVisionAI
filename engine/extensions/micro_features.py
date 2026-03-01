"""Micro-feature detection extension (NIR structural features only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from engine.app.analysis_types import ExtensionContext, ExtensionResult, ExtensionStatus


class MicroFeaturesExtension:
    """Detect lacunae/crypt/structural patches inside iris mask using YOLO."""

    name = "micro_features"
    version = "1"
    requires: list[str] = []
    optional_requires: list[str] = []

    def run(self, context: ExtensionContext) -> ExtensionResult:
        cfg = (
            context.config.get("extensions", {})
            .get(self.name, {})
        )
        if not bool(cfg.get("enabled", True)):
            return ExtensionResult(status=ExtensionStatus.SKIPPED, warning="Extension disabled by config.")

        weights_path = str(cfg.get("weights_path", "")).strip()
        if not weights_path:
            return ExtensionResult(
                status=ExtensionStatus.FAILED,
                warning="Missing YOLO weights path for micro_features extension.",
            )

        weights = Path(weights_path).expanduser()
        if not weights.exists():
            return ExtensionResult(
                status=ExtensionStatus.FAILED,
                warning=f"YOLO weights not found: {weights}",
            )

        iris_mask = (context.iris_mask > 0).astype(np.uint8)
        iris_points = np.where(iris_mask > 0)
        if iris_points[0].size == 0:
            return ExtensionResult(
                status=ExtensionStatus.SKIPPED,
                warning="Iris mask empty; micro feature detection skipped.",
            )

        y_min = int(np.min(iris_points[0]))
        y_max = int(np.max(iris_points[0])) + 1
        x_min = int(np.min(iris_points[1]))
        x_max = int(np.max(iris_points[1])) + 1

        crop_gray = context.grayscale_image[y_min:y_max, x_min:x_max]
        crop_iris = iris_mask[y_min:y_max, x_min:x_max]

        try:
            from ultralytics import YOLO  # type: ignore[import-not-found]
        except Exception as exc:
            return ExtensionResult(
                status=ExtensionStatus.FAILED,
                warning=f"ultralytics not available for micro_features: {exc}",
            )

        class_names = cfg.get(
            "class_names",
            {
                "0": "lacunae",
                "1": "crypt",
                "2": "structural_patch",
            },
        )

        model = YOLO(str(weights))
        result = model.predict(
            source=crop_gray,
            verbose=False,
            conf=float(cfg.get("confidence_threshold", 0.25)),
            iou=float(cfg.get("iou_threshold", 0.45)),
            imgsz=int(cfg.get("imgsz", 640)),
            augment=False,
            device=context.device,
        )[0]

        boxes_out: list[dict[str, Any]] = []
        box_area_sum = 0.0
        lacunae_count = 0
        crypt_count = 0

        if result.boxes is not None:
            for xyxy, score, cls_id in zip(
                result.boxes.xyxy.cpu().numpy(),
                result.boxes.conf.cpu().numpy(),
                result.boxes.cls.cpu().numpy(),
                strict=False,
            ):
                x1, y1, x2, y2 = [float(v) for v in xyxy]
                cx = int(round((x1 + x2) / 2.0))
                cy = int(round((y1 + y2) / 2.0))

                # Enforce iris-only detections by center-point mask membership.
                if cy < 0 or cy >= crop_iris.shape[0] or cx < 0 or cx >= crop_iris.shape[1]:
                    continue
                if crop_iris[cy, cx] == 0:
                    continue

                gx1 = max(0, int(round(x1)) + x_min)
                gy1 = max(0, int(round(y1)) + y_min)
                gx2 = min(context.grayscale_image.shape[1] - 1, int(round(x2)) + x_min)
                gy2 = min(context.grayscale_image.shape[0] - 1, int(round(y2)) + y_min)
                if gx2 <= gx1 or gy2 <= gy1:
                    continue

                label = class_names.get(str(int(cls_id)), f"class_{int(cls_id)}")
                if label == "lacunae":
                    lacunae_count += 1
                if label == "crypt":
                    crypt_count += 1

                area = float((gx2 - gx1) * (gy2 - gy1))
                box_area_sum += area
                boxes_out.append(
                    {
                        "bbox": [gx1, gy1, gx2, gy2],
                        "label": label,
                        "confidence": round(float(score), 6),
                    }
                )

        iris_area = float(np.count_nonzero(iris_mask))
        area_ratio = float(box_area_sum / iris_area) if iris_area > 0 else 0.0
        payload = {
            "micro_feature_boxes": boxes_out,
            "micro_feature_metrics": {
                "lacunae_count": lacunae_count,
                "crypt_count": crypt_count,
                "area_ratio": area_ratio,
                "density_per_sector": {},
            },
        }
        return ExtensionResult(
            status=ExtensionStatus.SUCCESS,
            payload=payload,
            model_version=str(cfg.get("model_version", "unknown")),
        )
