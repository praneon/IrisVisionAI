# Dataset Datasheet

## Source
- Dataset: CASIA-IrisV4 (NIR)
- Provider: Chinese Academy of Sciences Institute of Automation (CASIA)
- Access: Request via official contact (dataset not redistributable)

## Local storage structure
- `data/raw/casia_interval/` — original untouched images
- `data/working/images/` — cropped iris images used in experiments
- `data/working/masks/` — final corrected masks (PNG)
- `data/annotations/yolo_labels/` — YOLO .txt annotations
- `annotations/coco_segmentation.json` — COCO-format segmentation export
- `data/metadata.csv` — metadata per image

## Recommended splits
- Train: 70%
- Val: 15%
- Test: 15%
Stratify by subject_id when possible.

## Metadata fields
- `image_id`, `filename`, `subject_id`, `split`, `quality_score`, `illumination`, `annotator_ids`, `date_created`, `notes`

## Ethical & Legal
- Respect CASIA licensing — do not redistribute raw dataset.
- No PII or clinical data used.
- Use for research/educational purposes only.
