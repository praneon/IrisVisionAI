# Annotation Specification (NIR-Focused)

> **Status:** Protocol definition only  
> **Effective Version:** v0.3+  
> **Note:** No annotation work begins until subject-disjoint train/val/test splits are finalized.

---

## 1. Scope & Modality Constraints
- Applicable only to **Near-Infrared (NIR)** iris images
- Structural features only
- No color-, pigment-, or diagnostic-based annotations
- Research-only, non-diagnostic use

---

## 2. Segmentation Classes (Pixel Masks)

The following classes are annotated as **segmentation masks**:

- **`iris`**  
  Full visible iris area, excluding eyelids and eyelashes

- **`pupil`**  
  Pupil region only

- **`collarette`**  
  Collarette boundary region (thin circular band)

- **`scurf_rim`**  
  Outer iris boundary region, if clearly visible

- **`contraction_furrows`**  
  Major radial or concentric furrows only (ignore micro-texture)

---

## 3. Detection Classes (Bounding Boxes)

The following classes are annotated as **bounding boxes**:

- **`lacuna`**  
  Medium to large lacunae

- **`crypt`**  
  Structural cavities or darker pits

- **`patch`**  
  NIR-visible structural intensity variation

- **`artifact`** *(optional)*  
  Specular highlights, eyelash occlusion, or sensor artifacts  
  *(Excluded from model training)*

---

## 4. Annotation Rules

### Segmentation
- Use polygon masks for all regions
- Thin structures (collarette, furrows) must be annotated with **narrow, precise polygons**
- Masks must not include eyelids or eyelashes

### Detection
- Bounding boxes must tightly enclose the full extent of the feature
- Ignore features smaller than **10 × 10 pixels** at native resolution (320 × 280)

### General
- Do not annotate color-based features
- When uncertain, **do not annotate**
- Consistency is preferred over completeness

---

## 5. Quality Assurance (QA) Protocol

- 10% of samples are annotated by **two independent annotators**
- Metrics:
  - Segmentation: IoU ≥ 0.80
  - Detection labels: Cohen’s κ ≥ 0.75
- Disagreements resolved via review and protocol clarification

---

## 6. Annotation Metadata & Logging

- Dataset metadata (`data/metadata/metadata.csv`) remains **immutable**
- Annotation tracking is stored separately:
  - `docs/annotation_log.csv`
  - Fields: image_id, annotator_id, notes, revision_id
- All revisions must be auditable

---

## 7. Tooling Assumptions

- Annotation tool: **CVAT**
- Mask proposals may be generated using **SAM**
- Final annotations are **human-verified**
- Export formats:
  - Segmentation: COCO
  - Detection: YOLO

---

## 8. Exclusions & Non-Goals

- No medical or diagnostic interpretation
- No emotional or psychological labeling
- No color or toxicity claims
- No annotation before dataset split is frozen

---

