# 🧾 `ANNOTATION_SPEC.md` — *IrisVisionAI v0.4*

**Version:** v0.4 (FROZEN)  
**Scope:** Near-Infrared (NIR) iris images — CASIA-Iris-Interval  
**Purpose:** Pilot validation of structural annotation protocol  
**Annotation Type:** Polygon-based segmentation  
**Tooling:** CVAT  
**Reference:** `AMBIGUITY_REGISTRY.md (v0.4)`

---

## Purpose of This Document

This document defines **how structural iris features are annotated** during the **v0.4 pilot phase**.

It exists to:
- ensure consistent human decisions,
- prevent over-annotation,
- and make ambiguity handling explicit.

This document:
- **does define rules**
- **does not define thresholds for models**
- **does not claim anatomical certainty beyond visible structure**

---

## Structures in Scope

| Label Name | Description | Annotation Type |
|-----------|-------------|-----------------|
| `pupil` | Visible pupil boundary, regardless of shape | polygon |
| `iris` | Visible iris region between pupil and limbus, excluding occlusions | polygon |
| `collarette` | Inner structural boundary separating pupillary and ciliary zones (if visible) | polygon |
| `scurf_rim` | Thin, darker peripheral iris band near the limbus (if visible) | polygon |
| `contraction_furrows` | Broad, concentric arc-like furrows in the mid-periphery (if visible) | polygon |

---

## General Annotation Principles

- Annotate **only what is structurally visible**.
- When in doubt, **do not annotate**.
- Texture alone is **not** sufficient justification.
- Polygons should follow **anatomical edges**, not visual noise.
- No structure is required to appear in every image.

---

## Annotation Rules by Ambiguity Class

### A01 — Partial Eyelash Occlusion

- Do **not** annotate eyelashes or eyelids.
- Stop the `iris` polygon at the last visible boundary.
- Do **not** interpolate or guess behind occlusion.

---

### A02 — Reflection Overlapping Pupil Boundary

- Ignore specular reflections.
- Annotate the **true pupil boundary** as if the reflection were absent.
- Reflections are **not** annotated as structures.

---

### A03 — Low-Contrast Iris–Sclera Boundary

- Follow the most consistent visible limbal transition.
- Do not extend the iris polygon into sclera.
- If the boundary fades gradually, annotate conservatively.

---

### A04 — Discontinuous or Faint Collarette

- Annotate `collarette` **only if a structural boundary is clearly visible**.
- Partial or quadrant-limited visibility is acceptable.
- Skip annotation if the boundary blends into general iris texture.

---

### A05 — Texture vs Structural Feature Ambiguity

- Fine radial lines, grain, or mottling are **not** structures.
- Do not infer furrows or collarette from texture patterns alone.
- Structural annotation requires **clear edge continuity**.

---

### A06 — Shadow-Induced False Boundary

- Ignore shadow edges that mimic structural rings.
- Annotate only boundaries that persist independent of illumination gradients.

---

### A07 — Softened Pupil Edge Due to Illumination

- Annotate the pupil based on best visible estimate.
- Do not simplify or regularize the shape.
- Ellipse fitting is **not allowed**.

---

### A08 — Peripheral Iris Texture Fade

- Gradual texture loss toward the limbus does not imply a scurf rim.
- Annotate `scurf_rim` only if a **distinct, darker band** is visible.

---

## Structure-Specific Rules

### Pupil
- Always annotate if visible.
- Shape may be irregular.
- Ignore reflections and glare.

### Iris
- Annotate only visible iris tissue.
- Exclude occluded regions.
- Do not guess beyond eyelids or lashes.

### Collarette
- Conditional structure.
- Annotate only when a genuine structural boundary is apparent.
- Absence is a valid outcome.

### Contraction Furrows
- Annotate **only major, arc-shaped furrows**.
- Fine radial striations are excluded.
- Full circular rings are not expected.

### Scurf Rim
- Annotate only when separable from sclera.
- Thin, continuous darkening near the limbus.
- Skip if contrast is insufficient.

---

## Annotation Tooling Standards

- Use **polygon tool only**
- No brush, no bounding boxes
- Minimum **3 vertices per polygon**
- Polygons must be closed
- Adjust vertices manually; no auto-accept

---

## Quality Assurance Checklist (v0.4)

| Check | Requirement |
|-----|-------------|
| Boundary accuracy | Polygons follow visible anatomical edges |
| Occlusion handling | Iris excludes occluded regions |
| Structural restraint | No texture-only annotations |
| Consistency | Similar visibility → similar decisions |
| Format | CVAT polygon annotations only |

---

## v0.4 Scope Constraints

- Only pilot images are annotated in this version.
- Annotation rules are **frozen after pilot completion**.
- No new ambiguity classes may be added in v0.4.
- Observations for future refinement must go to `OBSERVATION_LOG.md`.

---

## Version Status

**v0.4 — LOCKED**  
Annotation protocol validated through pilot study.  
All future annotation must follow this specification exactly.

