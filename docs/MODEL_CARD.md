# Model Card

## Model Details
- Name: IrisVisionAI nnU-Net segmentation
- Purpose: Structural segmentation of NIR iris images
- Algorithms: nnU-Net for segmentation; YOLOv8 for detection; SAM for annotation assistance.

## Intended Use
- Research and educational use in computational iridology and biometric feature extraction.

## Limitations
- Trained on NIR data (CASIA). Not suitable for RGB images without retraining/adaptation.
- Not for clinical or diagnostic use.

## Training Data
- CASIA-IrisV4 (NIR), details in DATASET_DATASHEET.md.

## Metrics
- Report Dice, IoU, AP in experiments/metrics.

## Ethical Considerations
- Respect dataset licensing.
- No medical claims in outputs.
