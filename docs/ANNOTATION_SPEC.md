# Annotation Specification (NIR-focused)

## Segmentation classes (masks)
- `iris` — full iris area (exclude eyelids/eyelashes)
- `pupil` — pupil area
- `collarette` — collarette boundary region (thin ring)
- `scurf_rim` — outer rim if visible
- `contraction_furrows` — major radial/concentric furrows

## Detection classes (YOLO boxes)
- `lacuna` — medium to large lacunae
- `crypt` — cavities / darker structural pits
- `patch` — NIR-visible structural patch/intensity change
- `artifact` — specular highlight or eyelash occlusion (optional)

## Annotation rules
- Masks: draw polygon masks for rings and collarette. Thin rings should be narrow polygons.
- Boxes: tight bounding boxes around micro-feature extent.
- Minimum size threshold: ignore features smaller than 10×10 px at target resolution.
- Do not annotate color-based features (NIR cannot capture color).
- Use `artifact` class for occlusions to exclude during training.

## QA Protocol
- 10% random subset annotated by two annotators.
- Compute IoU for masks; target IoU >= 0.80.
- Compute Cohen's kappa for categorical labels; target >= 0.75.
- Maintain `data/metadata.csv` with annotator IDs and notes.
