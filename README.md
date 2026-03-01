<p align="center">
  <img src="banner.png" width="100%">
</p>

# IrisVisionAI - Research-Grade Structural Iris Analysis Pipeline (NIR)

A complete scientific pipeline for structural iris analysis using Near-Infrared (NIR) datasets such as CASIA-IrisV4.
This repository implements segmentation, micro-feature detection, clock-sector mapping, and interpretation layers (rule-based + VLM).


## Current Project Status (March 2026)

- ✔ Engine runtime hardening track is implemented and running under the unified `engine/` package.
- ✔ Extension runtime policy is active (execution order lock, timeout handling, dependency checks, namespaced outputs).
- ✔ Reproducibility artifacts are in place (`results.json`, `manifest.json`, `session_state.json`) with manifest hashing.
- ✔ Validation gates are active: engine tests pass and data consistency checks pass.
- ⏳ Final repository cleanup/staging pass is pending before release commit.
- ⏳ Production-scale annotation expansion and training phases remain pending by roadmap.

---

## Repository Use Case - What This Project Is For

This project provides a research-grade pipeline for computational iridology, focusing only on structural iris features visible under NIR.

### Anatomical Iris Segmentation
- Iris boundary
- Pupil boundary
- Collarette (derived, not directly segmented)
- Contraction furrows (derived/secondary)
- Scurf rim (derived/secondary)

### Micro-feature Detection (NIR-visible)
- Lacunae (medium-large)
- Crypts (medium-large)
- Structural patches

### Clock-Sector Mapping
Using polar transformation and iris center detection.

### Structured Output
- JSON map
- Visual overlays
- Structural interpretation (rule-based + VLM)

NOTE:
Color-based iridology (pigments, stages, chroma) is not possible in NIR and is deferred to v2.0 (RGB dataset).

---

## Primary Research Purpose

This project is meant for:
- Iris biometrics research
- Medical imaging analysis
- Structural iridology research (non-diagnostic)
- Feature extraction and mapping studies
- Building reproducible NIR iris workflows

It is NOT a diagnostic tool.

---

## Why NIR?

NIR offers:
- High structural clarity
- Consistent imaging
- Minimal glare/reflection

But it removes all iris color information.

This project is structural-only, not chromatic.

---

## What This Repository Includes

- Dataset preparation scripts (crop, QC, audit)
- Annotation protocol definitions
- SAM-assisted annotation helpers (assistive only)
- CVAT-based annotation workflow
- nnU-Net segmentation training
- YOLO-based micro-feature detection training
- Polar mapping and sector assignment
- Structural interpretation engine (rule-based + VLM)
- End-to-end pipeline CLI
- Documentation and experiment templates

---

## What This Repository Does NOT Include

These require RGB iris datasets (planned in v2.0):
- Pigment color interpretation
- Iris color typology
- Toxicity stages
- Psora/lymph pigments
- Chromatic rings
- Emotional/color analysis

---

## End-To-End Output

Given an input iris image:
1. Segmentation mask
2. Micro-feature detections
3. Sector mapping
4. Structural interpretation
5. Visual overlays
6. JSON + PDF export

---

## Pipeline Overview

```text
Dataset -> Annotation -> Segmentation -> Detection -> Sector Mapping -> Interpretation -> Reporting
```

---

## Repository Structure

```text
IrisAtlasAI/
|-- data/
|   |-- annotations/
|   |   `-- pilot_v0_4/
|   |-- metadata/
|   `-- splits/
|-- docs/
|-- engine/
|   |-- app/
|   |-- configs/
|   |-- core/
|   |-- extensions/
|   |-- models/
|   |   `-- nnunet_iris/
|   |-- tests/
|   `-- utils/
|-- scripts/
|-- DISCLAIMER.md
|-- LICENSE
|-- PATENTS
`-- README.md
```

---

## Documentation

All documentation is inside `/docs`.

- MODEL_OVERVIEW.md
- ANNOTATION_SPEC.md
- DATASET_DATASHEET.md
- PREPROCESSING.md
- TRAINING_RECIPES.md
- EVALUATION.md
- REPRODUCIBILITY.md
- MODEL_CARD.md
- VLM_PROMPTS.md

Each document is version-scoped and should not contradict the roadmap.

---

## VERSION CHECKLIST (Public Tracking)

Each version authorizes exactly one class of irreversible actions.

### v0.1 - Project Initialization (Complete)

| Task | Status |
| --- | --- |
| Define project scope and research intent | ✔ |
| Create repository and folder structure | ✔ |
| Infra vs project separation | ✔ |
| Add README and core documentation | ✔ |
| Add license, disclaimer, security policy | ✔ |
| Environment and tooling setup | ✔ |

---

### v0.2 - Dataset Preparation and Audit (Complete)

#### Dataset Scope and Policy

| Task | Status |
| --- | --- |
| Select primary dataset (CASIA-Iris-Interval) | ✔ |
| Lock dataset | ✔ |
| Archive non-primary datasets | ✔ |

#### Dataset Ingestion

| Task | Status |
| --- | --- |
| Download dataset | ✔ |
| Store raw data (unmodified) | ✔ |
| Verify directory consistency | ✔ |

#### Dataset Audit

| Task | Status |
| --- | --- |
| Count total images | ✔ |
| Inspect subject-wise structure | ✔ |
| Verify resolution and format | ✔ |
| Document filename conventions | ✔ |

#### Quality Control (QC)

| Task | Status |
| --- | --- |
| Detect corrupted images | ✔ |
| Flag blur/occlusion | ✔ |
| Log exclusions | ✔ |

#### Metadata

| Task | Status |
| --- | --- |
| Define metadata schema | ✔ |
| Generate metadata.csv | ✔ |
| Include QC flags | ✔ |

Restrictions:
- No dataset splitting
- No annotation
- No model training

---

### v0.3 - Dataset Split and Annotation Readiness (Complete)

#### Dataset Splits

| Task | Status |
| --- | --- |
| Subject-disjoint train/val/test split | ✔ |
| Fixed random seed (69) | ✔ |
| Save split manifest | ✔ |
| Generate split summary | ✔ |

#### Metadata Finalization

| Task | Status |
| --- | --- |
| Populate `split` column | ✔ |
| Preserve QC flags | ✔ |

#### Structural Readiness

| Task | Status |
| --- | --- |
| Prepare split-aware folder structure | ✔ |
| Write SPLITS.md documentation | ✔ |
| Explicitly defer annotation | ✔ |

Split is frozen permanently from this version onward.

---

### v0.4 - Annotation Protocol Validation (PILOT) [LOCKED]

Purpose:
Validate what is annotatable in NIR, define inclusion/exclusion rules, and freeze the structural taxonomy before scaling.

Scope:
- Pilot size: 10-30 images
- Dataset: CASIA-Iris-Interval (NIR)
- Tooling: CVAT (+ SAM assistive only)
- Output: canonical annotation archive
- NOT a training dataset

#### Annotation Definition and Rules

| Task | Status |
| --- | --- |
| Define structural labels (pupil, iris, collarette, scurf rim, contraction furrows) | ✔ |
| Define inclusion criteria per label | ✔ |
| Define explicit exclusion rules (radial fibers, crypt texture, artifacts) | ✔ |
| Document conditional labels (collarette/scurf rim/furrows) | ✔ |
| Freeze annotation granularity and polygon style | ✔ |

#### Pilot Annotation Execution

| Task | Status |
| --- | --- |
| Select visually diverse pilot images | ✔ |
| Create CVAT project and label schema | ✔ |
| Generate SAM proposals (assistive only, never auto-accept) | ⏳ |
| Manual polygon annotation in CVAT | ✔ |
| Annotate pupil and iris boundary | ✔ |
| Annotate collarette (only when clearly visible) | ✔ |
| Annotate contraction furrows (major, circumferential only) | ✔ |
| Annotate scurf rim (only when separable from sclera) | ✔ |
| Skip ambiguous structures | ✔ |

#### Quality Assurance (Pilot)

| Task | Status |
| --- | --- |
| Self-QA pass (frame-by-frame review) | ✔ |
| Check label consistency across images | ✔ |
| Verify no hallucinated structures | ✔ |
| Confirm conditional omission is consistent | ✔ |
| Log ambiguity and edge cases | ✔ |

#### Export and Archival

| Task | Status |
| --- | --- |
| Export annotations in CVAT for images 1.1 | ✔ |
| Preserve polygon geometry (no rasterization) | ✔ |
| Archive pilot annotations | ✔ |
| Freeze ANNOTATION_SPEC.md | ✔ |
| Write PILOT_NOTES.md | ✔ |

Restrictions:
- No dataset-wide annotation
- No COCO/YOLO/nnU-Net export
- No model training
- No label changes after lock

---

### v0.5 - Dataset-Scale Segmentation Annotation (PRODUCTION)

Purpose:
Create a research-grade segmentation dataset using the frozen v0.4 protocol.

#### Dataset Scope

| Task | Status |
| --- | --- |
| Select target dataset size (100-300 images minimum) | ⏳ |
| Ensure subject-disjoint splits (reuse v0.3) | ⏳ |
| Balance for occlusion/illumination/eye side | ⏳ |
| Lock image list for annotation | ⏳ |

#### Annotation Execution

| Task | Status |
| --- | --- |
| Reuse v0.4 label schema (no changes allowed) | ⏳ |
| Annotate pupil and iris boundary | ⏳ |
| Annotate collarette conditionally | ⏳ |
| Annotate scurf rim conditionally | ⏳ |
| Annotate contraction furrows conservatively | ⏳ |
| Enforce exclusion rules strictly | ⏳ |

#### Quality Assurance (Production)

| Task | Status |
| --- | --- |
| Periodic QA sampling (10-20%) | ⏳ |
| Drift detection vs v0.4 pilot | ⏳ |
| Remove over-annotated structures | ⏳ |
| Final dataset consistency check | ⏳ |

#### Export

| Task | Status |
| --- | --- |
| Export canonical CVAT archive | ⏳ |
| Freeze annotation dataset | ⏳ |
| Convert to COCO segmentation | ⏳ |
| Convert to nnU-Net format | ⏳ |

Restrictions:
- No interpretation
- No taxonomy claims

---

### v0.6 - Segmentation Model Training (nnU-Net)

Purpose:
Test whether machine learning can learn the defined iris structures.

| Task | Status |
| --- | --- |
| Generate segmentation masks from polygons | ⏳ |
| Validate mask alignment and class channels | ⏳ |
| Prepare nnU-Net dataset structure | ⏳ |
| Train baseline nnU-Net model | ⏳ |
| Evaluate Dice/IoU (internal only) | ⏳ |
| Perform visual sanity checks | ⏳ |
| Analyze failure cases | ⏳ |

---

### v0.7 - Micro-feature Annotation (YOLO)

Purpose:
Annotate secondary iris structures within segmented iris regions.

| Task | Status |
| --- | --- |
| Define lacuna/crypt taxonomy (NIR-visible only) | ⏳ |
| Restrict annotation to iris mask | ⏳ |
| Annotate medium-large micro-features | ⏳ |
| Export YOLO labels | ⏳ |
| QA pass | ⏳ |

---

### v0.8 - Detection Model Training

| Task | Status |
| --- | --- |
| Train YOLOv8/YOLOv10 | ⏳ |
| Evaluate AP/PR curves | ⏳ |
| Error analysis | ⏳ |
| Relabel if required | ⏳ |
| Save final weights | ⏳ |

---

### v0.9 - Sector Mapping Engine

| Task | Status |
| --- | --- |
| Iris center extraction | ⏳ |
| Polar transformation | ⏳ |
| Define clock-sector schema (12/24) | ⏳ |
| Map segmentations and detections to sectors | ⏳ |

---

### v0.10 - Rule-Based and VLM Interpretation (Explanation Only)

| Task | Status |
| --- | --- |
| Define structural interpretation rules | ⏳ |
| Implement rule engine | ⏳ |
| Generate textual summaries | ⏳ |
| Add VLM explanation layer | ⏳ |

Restrictions:
- No diagnostic claims
- No decision-making

---

### v1.0 - Alpha Release (Complete Pipeline)

| Task | Status |
| --- | --- |
| End-to-end pipeline runner | ⏳ |
| Visual overlays | ⏳ |
| JSON and PDF reports | ⏳ |
| Reproducibility validation | ⏳ |
| Final documentation | ⏳ |

---

## Governing Rule (FINAL)

Any step injecting human knowledge occurs only during annotation phases (v0.4-v0.5).
Any step injecting machine learning occurs only after annotation datasets are frozen.

This ensures methodological validity, reproducibility, and scientific integrity.

---

## v2.0 - RGB Expansion (TBA)

Requires color-visible iris datasets.

Planned features:
- Pigment color analysis
- Iris color typing
- Toxicity and stress rings
- Chromatic staging
- Emotional/color structures

---

## Current Limitations

- NIR images contain no color information
- NIR-trained models do not generalize to RGB
- Fine micro-features may be ambiguous in NIR
- No medical diagnosis intended
- CASIA datasets cannot be redistributed

---

## Citation

"Portions of the research in this work use the CASIA-IrisV4 dataset collected by the Chinese Academy of Sciences' Institute of Automation."

---

## Contributing

- PRs welcome
- Use feature branches
- Follow formatting (black, ruff)
- Add tests for new code

---

## Author

Vishal N
Founder - Praneon, IrisVisionAI
BNYS Final Year, Intern

---

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![PyTorch](https://img.shields.io/badge/Framework-PyTorch-red.svg)
![Model-nnUNet](https://img.shields.io/badge/Segmentation-nnU--Net-green.svg)
![YOLO](https://img.shields.io/badge/Detection-YOLOv8/YOLOv10-blue.svg)
![Status](https://img.shields.io/badge/Status-Active--Development-green)
