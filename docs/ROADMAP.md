# Project Roadmap

This roadmap reflects the execution order used in this project.
It keeps research flow, code flow, and release flow aligned.

## Current snapshot (March 2026)

- This repository is the research runtime and documentation source of truth.
- Desktop packaging/UI delivery is maintained in an external app stack path.
- Annotation pilot protocol is locked; model phases are staged after that lock.

## Completed phases

### v0.1 — Infrastructure foundation
Delivered:
- workspace split between private infra and public repo
- baseline repo structure, policy files, and setup baseline

### v0.2 — Dataset intake and datasheet
Delivered:
- CASIA-Iris-Interval selected and locked for active phase
- dataset audit and metadata baseline
- data policy boundaries documented

### v0.3 — Subject split freeze
Delivered:
- subject-level split manifest
- split assignments recorded in metadata
- leakage-prevention policy locked

### v0.4 — Annotation protocol lock
Delivered:
- ambiguity registry
- structural annotation specification
- pilot annotation baseline exported

## Active phase

### v0.5 — Engine-first architecture hardening
Status: release-candidate

Completed in this phase:
- importable `engine.run_analysis(...)` runtime surface
- extension runtime scaffolding and namespaced outputs
- single-engine code root (`engine/`) with unified core/config/tests
- deterministic extension execution order and status locking
- reproducibility artifacts per run (`results.json`, `manifest.json`, `session_state.json`)
- manifest hashing and environment/config snapshot capture
- data consistency gate (`scripts/check_data_consistency.py`)

Remaining to close this phase:
- final git-tree cleanup/commit hygiene pass before release tag
- one final release-gate execution on clean working tree

## Next phases

### v0.6 — Segmentation baseline training
Planned:
- training dataset conversion/validation
- baseline segmentation training
- metric + overlay evaluation package

### v0.7 — Micro-feature detection pipeline
Planned:
- micro-feature annotation QA and dataset prep
- detector training and error analysis

### v0.8 — Sector mapping validation
Planned:
- deterministic geometry validation
- sector-level density outputs and regression checks

### v0.9 — Interpretation layer hardening
Planned:
- deterministic summary stability checks
- language safety constraints for explanatory outputs

### v1.0 — Reproducible alpha release
Planned:
- versioned end-to-end pipeline run
- frozen docs + frozen evaluation artifacts
- release checklist closure

## Governance rules

- No phase is considered complete without its documentation update.
- Cross-phase work is allowed only if explicitly tracked in phase notes.
- Any change to locked phase behavior must be recorded as a new versioned change.

## Release-gate commands

```bash
PYTHONDONTWRITEBYTECODE=1 pytest -q engine/tests -p no:cacheprovider
python3 scripts/check_data_consistency.py
```
