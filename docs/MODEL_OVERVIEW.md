# Model Overview

This page summarizes the model components used (or planned) in IrisAtlasAI.

## Segmentation

Primary baseline:
- nnU-Net 2D for structural mask prediction

Expected labels:
- iris
- pupil
- collarette
- scurf rim
- contraction furrows

Output:
- per-pixel multi-class masks

## Annotation assist

SAM is used as an assistive proposal tool only.
Final labels are human-corrected in CVAT.

## Micro-feature detection

Candidate line:
- YOLO family (starting from lightweight variants)

Target objects:
- lacunae
- crypts
- structural patches

Output:
- bounding boxes, class labels, confidence

## Mapping layer

OpenCV-based geometry transforms are used for polar unwrap and sector assignment.

## Interpretation layer

Two modes:
- deterministic rule-based summary
- optional VLM-expanded explanation text

Policy:
- non-diagnostic language only
- structural evidence must remain traceable to deterministic outputs
