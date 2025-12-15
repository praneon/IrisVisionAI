# Model Overview

## Segmentation
**Model:** nnU-Net (2D)
- Purpose: Medical-grade segmentation of iris anatomical structures.
- Inputs: NIR iris crop (grayscale), typical processing to 512×512 patches.
- Outputs: Per-pixel masks for classes:
  - iris
  - pupil
  - collarette
  - scurf_rim
  - contraction_furrows
- Loss: Dice + CrossEntropy (nnU-Net defaults)
- Metrics: Dice (per-class), mean IoU, Hausdorff distance (optional)
- Notes: Use nnU-Net's auto-configuration. Adjust batch size for GPU limitations.

## Annotation Assistant
**Model:** SAM (Segment Anything Model)
- Purpose: Propose masks to accelerate annotation.
- Workflow: SAM proposals -> import into CVAT -> human corrections -> final masks.

## Optional Advanced Segmentation
**Model:** Mask2Former
- Purpose: Transformer-based instance/panoptic segmentation comparison.
- Use only for ablation or if compute/resources permit.

## Detection (Micro-features)
**Model:** YOLOv8-N / YOLOv10-N (Ultralytics)
- Purpose: Detect lacunae, crypts, structural patches as bounding boxes.
- Inputs: Iris crops (optionally with segmentation overlays)
- Outputs: Bounding boxes with class labels
- Metrics: AP@0.5, AP@0.5:0.95, AP_small, Precision/Recall
- Notes: Start with -n (nano) model for GTX1650; scale up to -s if GPU available.

## Polar/Spatial Transform
- Implementation: OpenCV remap for polar unwrapping; optional STN module.
- Purpose: Convert circular iris textures into unwrapped strips; assist sector mapping.

## Interpretation Engines
### Rule-based
- Deterministic mapping from structural JSON to templated sentences.
- Provides reproducible, auditable outputs.

### VLM-based
- Candidate models: Florence-2, LLaVA, Qwen-VL.
- Purpose: Produce contextualized natural-language descriptions of structural findings.
- Note: Use for explanation only, avoid medical claims.
