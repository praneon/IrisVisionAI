# IrisVisionAI — Project Roadmap

This roadmap defines the **ordered, versioned progression** of the IrisVisionAI
research pipeline. Each version introduces a **single class of irreversible work**
and is locked once completed.

The roadmap is designed to preserve:
- methodological clarity,
- reproducibility,
- and long-term extensibility.

---

## v0.1 — Infrastructure & Project Setup ✅

**Purpose:** Establish a stable research workspace.

Key outcomes:
- Repository structure finalized
- Separation of `infra/` (private) and `projects/` (public) enforced
- Environment setup documented
- Licensing, security, and disclaimers added

**Status:** Complete and locked.

---

## v0.2 — Dataset Preparation & Documentation ✅

**Purpose:** Select, audit, and document the dataset without modifying it.

Key outcomes:
- CASIA-Iris-Interval selected as the sole dataset
- Other datasets explicitly excluded
- Dataset audited for corruption and basic quality issues
- Metadata schema defined
- `DATASET_DATASHEET.md` written and frozen

**Restrictions:**
- No dataset splitting
- No annotation
- No modeling

**Status:** Complete and locked.

---

## v0.3 — Dataset Split & Annotation Readiness ✅

**Purpose:** Prepare the dataset for annotation without injecting labels.

Key outcomes:
- Subject-disjoint train/val/test split created
- Split logic documented
- Metadata updated with split assignments
- Annotation explicitly deferred

**Restrictions:**
- No annotation
- No modeling

**Status:** Complete and locked.

---

## v0.4 — Structural Segmentation Annotation (CVAT + SAM) ✅

**Purpose:** Define and validate human annotation protocol.

Key outcomes:
- Ambiguity space explored and frozen
- `AMBIGUITY_REGISTRY.md` finalized
- `ANNOTATION_SPEC.md` written and validated
- Pilot annotations completed
- Annotation protocol locked

**Restrictions:**
- No model training
- No automatic labeling

**Status:** Complete and locked.

---

## v0.5 — Structural Segmentation Model Training (nnU-Net)

**Purpose:** Train a baseline segmentation model on validated annotations.

Planned outcomes:
- Convert annotations to nnU-Net format
- Verify preprocessing correctness
- Train nnU-Net segmentation model
- Evaluate using Dice, IoU, and visual inspection
- Save model checkpoints and configs

**Restrictions:**
- No micro-feature detection
- No interpretation logic

**Status:** Planned.

---

## v0.6 — Micro-feature Annotation (Detection Targets)

**Purpose:** Define and annotate smaller structural features.

Planned outcomes:
- Define lacunae / crypt taxonomy
- Annotate micro-features on segmented irises
- Export detection labels (YOLO format)
- Perform QA review

**Status:** Planned.

---

## v0.7 — Micro-feature Detection Model Training (YOLO)

**Purpose:** Train detection models for micro-structures.

Planned outcomes:
- Train YOLO-based detector
- Evaluate AP, precision, recall
- Analyze small-object performance
- Save final detection weights

**Status:** Planned.

---

## v0.8 — Iris Sector Mapping Engine

**Purpose:** Map structures to anatomical clock sectors.

Planned outcomes:
- Iris center estimation
- Polar coordinate transformation
- Sector definition (12 / 24)
- Mapping of segmentation and detection outputs

**Status:** Planned.

---

## v0.9 — Rule-Based Structural Interpretation

**Purpose:** Produce structured, non-diagnostic interpretations.

Planned outcomes:
- Define interpretation rules
- Implement rule engine
- Generate structured textual summaries
- Validate logical consistency

**Status:** Planned.

---

## v0.10 — Vision-Language Explanation Layer

**Purpose:** Generate human-readable explanations.

Planned outcomes:
- Select vision-language model
- Define prompt templates
- Generate explanatory text from structured outputs
- Combine with rule-based interpretations

**Restrictions:**
- No diagnostic claims
- Explanation only

**Status:** Planned.

---

## v1.0 — Alpha Pipeline Release

**Purpose:** Deliver a complete, reproducible research pipeline.

Planned outcomes:
- End-to-end CLI or runner
- Visual overlays and reports
- JSON and PDF outputs
- Reproducibility validation
- Final documentation pass

**Status:** Planned.

---

## Governing Principle

> Human knowledge enters before machine learning.  
> Machine learning enters before interpretation.  
> No version violates this order.

This roadmap is **authoritative**. Deviations require a new version and
explicit documentation.

