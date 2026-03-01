# Dataset Datasheet (v0.2 Freeze)

## Identity

- Dataset: CASIA-Iris-Interval
- Modality: NIR grayscale iris images
- Source: CASIA Iris Database
- Use in this project: research-only structural analysis (non-diagnostic)

## Scope decision in v0.2

- Primary dataset: CASIA-Iris-Interval
- Other CASIA subsets: excluded for this phase
- External datasets (PolyU, IITD, ND-GFI): not active in v0.2
- v0.2 status: frozen

## Subject and image summary

- Subjects: 249
- Images: 2639
- Format: JPG
- Resolution: 320x280
- Eye side: left and right, depending on subject availability

## Organization

Data follows subject and eye hierarchy with original naming retained.
No raw image renaming or modification is applied in-place.

## Quality control in v0.2

- Corruption checks: completed
- Corrupt files found: none in v0.2 audit
- Blur/occlusion flags: captured in metadata where applicable
- Hard exclusion: not applied at this phase

## Metadata

Primary file:
- `data/metadata/metadata.csv`

Expected record granularity:
- one row per image

Typical fields:
- subject id
- eye side
- image index
- resolution and quality flags
- split assignment (initially unset during v0.2)

## Leakage policy

- Split unit is subject, not image.
- A subject may appear in only one split.
- Left/right images of same subject are treated as linked for split purposes.

## Known limitations

- No demographic attributes bundled in source dataset metadata
- Uneven per-subject sample counts
- Dataset is not a clinical ground truth source

## Version note

This datasheet documents the v0.2 data decision state.
Later pipeline phases can consume the dataset but should not silently alter this baseline.
