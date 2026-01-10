# Training Recipes — IrisVisionAI

This document captures **practical training guidance** for the models used in
IrisVisionAI. These are **recommended starting points**, not rigid prescriptions.
All training should prioritize reproducibility and clarity over aggressive tuning.

---

## 1. nnU-Net — Structural Segmentation

### Purpose
Train a baseline segmentation model for core iris structures using
human-validated annotations.

---

### Dataset Preparation

- Convert CVAT / COCO-style polygon annotations into nnU-Net’s dataset structure.
- Use a dedicated conversion script, for example:
```

convert_coco_to_nnunet.py

````
- Before training, verify:
- correct image–mask alignment
- correct class indexing
- dataset integrity via nnU-Net checks

---

### Example Commands

> Exact CLI syntax depends on the nnU-Net installation and version.

```bash
nnUNet_plan_and_preprocess -t TASK_ID --verify_dataset_integrity
nnUNet_train 2d nnUNetTrainerV2 TaskXXX_FOLD0
````

---

### Training Notes

* **Optimizer:** AdamW (nnU-Net default)
* **Learning Rate:** auto-configured by nnU-Net (typically ~1e-3 effective)
* **Epochs:** ~200–400 (monitor convergence)
* **Batch Size:** determined by available GPU memory
* **Logging:** TensorBoard (default), Weights & Biases optional

Manual hyperparameter tuning should be avoided until a stable baseline is
established.

---

## 2. YOLOv8 — Micro-feature Detection

### Purpose

Detect small iris structures (e.g., lacunae, crypts) after segmentation.

---

### Dataset Preparation

* Prepare annotations in **YOLO detection format**
* Define dataset paths and class names in `yolo_dataset.yaml`
* Bounding boxes should be conservative and human-verified

---

### Example Training Command

```bash
yolo task=detect \
     mode=train \
     model=yolov8n.pt \
     data=annotations/yolo_dataset.yaml \
     imgsz=640 \
     epochs=100 \
     batch=16
```

---

### Hardware Considerations

* For limited GPUs (e.g., GTX 1650):

  * use smaller models (`yolov8n`)
  * reduce batch size if needed
  * avoid very large input resolutions

---

### Evaluation Focus

* **AP@0.5**
* **AP@0.5:0.95**
* **AP_small** (critical for fine structures)

Metric reporting must be paired with visual inspection.

---

## 3. Vision–Language Model (VLM)

### Purpose

Generate **human-readable explanations** from structured pipeline outputs.

---

### Initial Approach

* Begin with **prompt engineering only**
* Inputs typically include:

  * structured JSON outputs
  * a small visual overlay image
* Outputs must remain descriptive and **non-diagnostic**

---

### Fine-Tuning (Optional)

* Fine-tuning is not required for v0.x
* Reliable fine-tuning requires:

  * substantial curated data
  * significant compute resources
  * careful evaluation to avoid hallucination

VLM fine-tuning should only be considered after the full pipeline is stable.

---

## General Training Principles

* Establish baselines before optimization
* Prefer reproducibility over marginal gains
* Save:

  * configuration files
  * random seeds
  * evaluation artifacts
* Document any deviations from these recipes explicitly

```


