# Evaluation Metrics & Protocol

This document defines the evaluation methodology used across the
segmentation, detection, mapping, and interpretation stages of IrisVisionAI.

The emphasis is on **transparent reporting**, **failure visibility**, and
**research-grade validation**, not leaderboard optimization.

---

## 1. Segmentation Evaluation

Segmentation models are evaluated on **structural accuracy**, both
quantitatively and qualitatively.

### Quantitative Metrics

- **Dice Coefficient**  
  - Computed per class (`pupil`, `iris`, `collarette`, `scurf_rim`, `contraction_furrows`)
  - Reported as mean ± standard deviation

- **Intersection over Union (IoU)**
  - Mean IoU across classes
  - Per-class IoU for error analysis

- **Pixel-wise Precision & Recall**
  - Useful for detecting over-segmentation vs under-segmentation
  - Reported per class

### Qualitative Evaluation

- Save **visual grids** showing:
  - Best-performing samples
  - Worst-performing samples
  - Typical (median) cases
- Overlays must include:
  - Ground truth mask
  - Predicted mask
  - Difference visualization

Visual results are considered mandatory, not optional.

---

## 2. Detection Evaluation (Micro-features)

Detection models (YOLO-based) are evaluated with standard object detection
metrics, with special attention to small structures.

### Quantitative Metrics

- **AP@0.5**
- **AP@0.5:0.95**
- **AP_small**
  - Critical for small lacunae, crypts, and fine structural features
- **Precision and Recall**
  - Reported per class
- **Confusion Matrix**
  - Used to analyze systematic misclassification between feature types

### Error Analysis

- False positives vs false negatives analyzed separately
- Class imbalance effects explicitly discussed
- Representative failure cases visualized

---

## 3. Mapping & Interpretation Evaluation

Mapping and interpretation are evaluated differently from ML models, as they
are partially rule-based.

### Sector Mapping

- **Unit tests** for polar coordinate and sector assignment
- Synthetic test points with known sector labels
- Edge-case testing at sector boundaries

### Interpretation Layer

- **Human expert qualitative review**
  - Focus on structural consistency
  - No diagnostic or clinical claims evaluated

- Evaluation is descriptive, not statistical

---

## 4. Reporting & Artifacts

- All metrics, plots, and qualitative examples are stored under:
        experiments/metrics/
- Reports must include:
- Metric tables
- Visual examples
- Notes on known failure modes

No single scalar score is treated as definitive.

---

## 5. Evaluation Philosophy

- Prefer **clarity over compression**
- Always pair metrics with visuals
- Explicitly document weaknesses
- Avoid over-interpretation of numerical scores

Evaluation exists to **understand model behavior**, not to claim optimality.

