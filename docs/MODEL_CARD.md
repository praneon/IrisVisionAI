# Model Card (Working Draft)

## Model family

- Segmentation: nnU-Net baseline
- Detection: YOLO baseline for micro-features
- Annotation assistance: SAM (human-in-the-loop)

## Intended use

Research use for structural iris analysis on NIR imagery.
Not a clinical diagnostic system.

## Out of scope

- medical diagnosis
- risk prediction
- treatment decision support

## Data scope

- Primary source: CASIA-Iris-Interval (NIR)
- See `DATASET_DATASHEET.md` for dataset constraints and known limitations

## Evaluation expectations

- segmentation: Dice/IoU + visual checks
- detection: AP and per-class behavior
- interpretation: consistency and language safety checks

## Safety and ethics notes

- respect dataset licensing
- avoid diagnostic claims
- document failure cases and uncertainty explicitly
