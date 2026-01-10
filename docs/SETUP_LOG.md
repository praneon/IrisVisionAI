# IrisVisionAI — Setup Log (v0.1)

This document records the **initial environment setup and infrastructure
decisions** made during v0.1. It serves as a historical log, not an active
instruction manual.

---

## Version

**v0.1 — Infrastructure & Project Scaffold**

Status: **Frozen**

---

## Environment

- **Operating System:** Ubuntu  
- **Python:** 3.10  
- **Conda Environment:** `irisvision`  
- **GPU:** NVIDIA GTX 1650  
- **PyTorch:** CUDA-enabled build  

### Installed Frameworks & Tools

- **YOLOv8**
  - Installed
  - Sanity-checked with test inference

- **nnU-Net v1**
  - Installed
  - Environment configured
  - Not trained at this stage

- **SAM (Segment Anything Model)**
  - Installed
  - Imports and basic usage verified

No training or dataset-dependent execution occurred in v0.1.

---

## Folder Strategy

The workspace was intentionally split to separate **private infrastructure**
from the **public project repository**.

- **Conda environments & runtimes:**  
  `/data/workspace/envs`

- **nnU-Net workspaces (raw / preprocessed / results):**  
  `/data/workspace/nnunet*`

- **External datasets (licensed, non-redistributable):**  
  `/data/workspace/datasets`

- **Project repository (code & docs only):**  
  `/data/workspace/projects/IrisVisionAI`

This separation is a foundational design decision and is preserved
through all subsequent versions.

---

## Data Policy

- No licensed datasets are stored in the Git repository
- CASIA, PolyU, and other datasets are referenced indirectly via
  `configs/paths.yaml`
- The repository remains lightweight, portable, and legally compliant

---

## Status Summary

- ✔ Infrastructure complete  
- ✔ Repository structure defined and frozen  
- ✔ Environment verified for downstream work  

**Ready to proceed to v0.2 — Dataset Preparation & Audit**

---

_Last updated: v0.4_

