# CI Suggestions — GitHub Actions

This document outlines **recommended (not mandatory)** continuous integration workflows
for the IrisVisionAI repository.

The goal of CI here is **sanity, consistency, and safety** — not heavy training or benchmarking.

---

## Recommended Workflows

### 1. `lint-and-test.yml`

**Purpose:**  
Catch formatting issues, obvious bugs, and broken imports early.

**Triggers:**  
- Pull requests  
- Pushes to `main`

**Suggested steps:**
- Set up Python (match project version)
- Install dependencies
- Run:
  - `black --check`
  - `ruff`
  - unit tests (if present)

**Notes:**
- Keep this fast
- No dataset access required
- No GPU required

---

### 2. `docker-build.yml`

**Purpose:**  
Ensure the Dockerfile stays valid and reproducible.

**Triggers:**  
- Pushes to `main`
- Manual trigger (workflow_dispatch)

**Suggested steps:**
- Build Docker image
- Optionally tag with commit SHA
- Do **not** push images unless explicitly intended

**Notes:**
- This validates environment assumptions
- No training should happen here

---

### 3. `smoke-train.yml` (Optional)

**Purpose:**  
Detect pipeline breakage (I/O, configs, scripts) using a minimal run.

**Triggers:**  
- Manual trigger only (`workflow_dispatch`)

**Suggested behavior:**
- Use a **very small synthetic or dummy sample**
- Run:
  - preprocessing
  - model initialization
  - 1-epoch forward pass
- Exit immediately after sanity check

**Important constraints:**
- Do **not** use full datasets
- Do **not** download CASIA or any licensed data
- Do **not** run full training

This workflow is for **pipeline validation only**, not performance.

---

## Secrets & External Services

- Store API keys (e.g. Weights & Biases) as **GitHub Secrets**
- Never hardcode credentials
- CI should run correctly even if optional services are disabled

---

## Explicit Non-Goals

CI workflows must **never**:
- Commit or upload model weights
- Store datasets or images
- Perform large-scale training
- Act as an evaluation benchmark

---

## Philosophy

CI exists here to:
- protect reproducibility
- prevent accidental breakage
- keep contributions clean

Anything expensive, data-heavy, or exploratory belongs **outside CI**.

