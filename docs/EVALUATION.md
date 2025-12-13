# Evaluation Metrics & Protocol

## Segmentation Metrics
- Dice coefficient (per class)
- Mean IoU
- Pixel-wise Precision & Recall
- Save visual grids of best/worst predictions

## Detection Metrics
- AP@0.5
- AP@0.5:0.95
- AP_small (important for small lacunae)
- Precision, Recall per class
- Confusion matrix analysis

## Mapping & Interpretation
- Unit tests for sector assignment (synthetic points)
- Human expert qualitative review for interpretation outputs
- Report metrics and examples in `experiments/metrics/`
