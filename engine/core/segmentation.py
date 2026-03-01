"""Segmentation module using nnU-Net v2 inference for structural iris labels."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np


CANONICAL_CLASS_LABELS = {
    "background": 0,
    "pupil": 1,
    "iris": 2,
    "collarette": 3,
    "scurf_rim": 4,
    "contraction_furrows": 5,
}


class IrisSegmentationEngine:
    """Run deterministic nnU-Net inference and return a single-channel label mask."""

    def __init__(self, model_config: Dict[str, Any]) -> None:
        self.model_config = model_config
        self.model_version = model_config.get("model_version", "unknown")
        self.device = model_config.get("device", "cpu")
        self._set_deterministic()
        self._validate_canonical_class_map()
        self._predictor = self._load_predictor()

    @staticmethod
    def _set_deterministic() -> None:
        """Set deterministic torch flags and seeds for reproducible output."""
        try:
            import torch
        except Exception:
            return

        torch.manual_seed(0)
        np.random.seed(0)
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def _normalized_class_labels(self) -> Dict[str, int]:
        class_labels = dict(self.model_config.get("class_labels", {}))
        if "furrows" in class_labels and "contraction_furrows" not in class_labels:
            class_labels["contraction_furrows"] = class_labels.pop("furrows")
        return {str(key): int(value) for key, value in class_labels.items()}

    def _validate_canonical_class_map(self) -> None:
        normalized = self._normalized_class_labels()
        if normalized != CANONICAL_CLASS_LABELS:
            raise ValueError(
                f"class_labels must exactly match canonical v0.5 mapping: {CANONICAL_CLASS_LABELS}"
            )

    def _load_predictor(self):
        """Instantiate an nnU-Net predictor once per process."""
        try:
            import torch
        except Exception as exc:
            raise ImportError("torch is required for segmentation inference.") from exc

        self._ensure_nnunet_env_vars()
        model_folder = self._validate_model_folder()

        try:
            from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
        except ImportError as exc:
            raise ImportError(
                "nnunetv2 is required for segmentation inference. Install from requirements.txt"
            ) from exc

        predictor = nnUNetPredictor(
            tile_step_size=self.model_config.get("tile_step_size", 0.5),
            use_gaussian=True,
            use_mirroring=False,
            perform_everything_on_device=self.model_config.get(
                "perform_everything_on_device", True
            ),
            device=torch.device(self.device),
            verbose=False,
            verbose_preprocessing=False,
            allow_tqdm=False,
        )

        predictor.initialize_from_trained_model_folder(
            model_training_output_dir=str(model_folder),
            use_folds=self.model_config.get("folds", [0]),
            checkpoint_name=self.model_config.get("checkpoint_name", "checkpoint_final.pth"),
        )
        return predictor

    @staticmethod
    def _engine_root() -> Path:
        return Path(__file__).resolve().parents[1]

    def _validate_model_folder(self) -> Path:
        model_folder_raw = self.model_config.get("model_folder")
        if not model_folder_raw:
            raise ValueError("model_folder is required in model_config.json")

        model_folder = Path(model_folder_raw)
        if not model_folder.is_absolute():
            model_folder = (self._engine_root() / model_folder).resolve()

        dataset_json = model_folder / "dataset.json"
        plans_json = model_folder / "plans.json"
        if not model_folder.exists():
            raise FileNotFoundError(
                f"Model folder not found: {model_folder}. "
                "Place exported nnU-Net model files there or update model_config.json:model_folder."
            )
        if not dataset_json.exists() or not plans_json.exists():
            raise FileNotFoundError(
                f"Model folder is incomplete: {model_folder}. "
                "Required files missing: dataset.json and/or plans.json."
            )
        return model_folder

    @staticmethod
    def _ensure_nnunet_env_vars() -> None:
        base = Path.home() / ".irisatlasai" / "nnunet"
        env_paths = {
            "nnUNet_raw": base / "raw",
            "nnUNet_preprocessed": base / "preprocessed",
            "nnUNet_results": base / "results",
        }
        for key, path in env_paths.items():
            if not os.environ.get(key):
                path.mkdir(parents=True, exist_ok=True)
                os.environ[key] = str(path)

    def infer(self, gray_image: np.ndarray) -> np.ndarray:
        """Run segmentation inference and return labels [0..5] as uint8 mask."""
        resized = cv2.resize(
            gray_image,
            tuple(self.model_config.get("input_size", [256, 256])),
            interpolation=cv2.INTER_AREA,
        )

        image_float = resized.astype(np.float32) / 255.0
        image_4d = image_float[None, None, ...]

        segmentation = self._predictor.predict_single_npy_array(
            input_image=image_4d,
            image_properties={"spacing": np.array([1.0, 1.0, 1.0])},
            segmentation_previous_stage=None,
            output_file_truncated=None,
            save_or_return_probabilities=False,
        )

        if isinstance(segmentation, tuple):
            segmentation = segmentation[0]

        mask = np.asarray(segmentation, dtype=np.uint8)
        mask = cv2.resize(
            mask,
            (gray_image.shape[1], gray_image.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )

        if mask.ndim != 2:
            raise ValueError("Segmentation mask must be single-channel")

        if not set(np.unique(mask)).issubset(set(CANONICAL_CLASS_LABELS.values())):
            raise ValueError("Unexpected labels found in segmentation output")

        return mask
