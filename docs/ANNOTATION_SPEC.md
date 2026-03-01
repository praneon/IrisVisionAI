# Annotation Specification 

Scope:
- Dataset: CASIA-Iris-Interval
- Modality: NIR grayscale
- Tool: CVAT polygon annotation
- Phase: v0.4 pilot protocol validation

Reference:
- `AMBIGUITY_REGISTRY.md`

## Goal

Define how we annotate visible iris structures consistently.
The priority is consistency and restraint, not maximum label density.

## In-scope labels

- `pupil`: visible pupil boundary
- `iris`: visible iris tissue between pupil and limbus
- `collarette`: inner structural ring when clearly visible
- `scurf_rim`: darker peripheral band near limbus when clearly visible
- `contraction_furrows`: broad arc-like furrows when clearly visible

## Core principles

- Annotate only what is structurally visible.
- Do not guess behind occlusion.
- Do not annotate texture unless clear structural boundaries exist.
- Conservative omission is preferred over speculative labeling.

## Ambiguity handling rules

### A01 Partial eyelash occlusion
- Do not annotate eyelashes/eyelids.
- Stop iris boundary at last visible region.
- No interpolation through occlusion.

### A02 Reflection crossing pupil edge
- Ignore reflection pixels as structures.
- Trace the best estimate of true pupil boundary.

### A03 Weak iris–sclera contrast
- Follow consistent visible limbus transition.
- Do not push mask into sclera.
- If uncertain, annotate conservatively.

### A04 Faint/discontinuous collarette
- Annotate collarette only where boundary is clearly visible.
- Partial collarette annotation is valid.
- Skip if it blends into texture.

### A05 Texture vs structure confusion
- Fine grain/radial texture is not a structural label.
- Require clear edge continuity for structural labels.

### A06 Shadow-induced false boundary
- Ignore boundaries that track illumination/shadow artifacts.

### A07 Soft pupil edge
- Trace visible contour without geometric regularization.
- Do not fit idealized ellipse shapes.

### A08 Peripheral texture fade
- Fading texture alone does not imply scurf rim.
- Require a separable dark peripheral band for `scurf_rim`.

## Structure-specific notes

- Pupil: annotate whenever visible.
- Iris: annotate visible tissue only; exclude occluded segments.
- Collarette: optional/conditional.
- Furrows: only major arc-like furrows, not fine lines.
- Scurf rim: only when distinct from limbus/sclera transition.

## Tooling constraints

- Polygon tool only
- No brush masks, no bbox-only labels
- Closed polygons only
- Minimum three vertices per polygon
- Manual vertex correction required

## QA checklist

- Polygons follow visible anatomy
- Occluded regions are not hallucinated
- Texture-only structures are excluded
- Similar cases get similar decisions
- Export format is valid CVAT polygon output

## Version lock

v0.4 annotation protocol is frozen.
Changes require a new versioned spec update.
