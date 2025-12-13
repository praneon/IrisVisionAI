# Repository Guide

## Naming Conventions
- Images: `img_<subject>_<session>_<index>.jpg`
- Masks: `img_<subject>_<session>_<index>_mask.png`
- YOLO labels: `img_<subject>_<session>_<index>.txt`
- Checkpoints: `experiments/exp-0001/checkpoints/nnunet_best.pth`
- Results: `results/<image_id>_struct.json`

## Folder overview
- `data/` — raw and working data
- `src/` — code modules
- `docs/` — documentation
- `experiments/` — experiment configs and checkpoints
- `notebooks/` — EDA and experiments
- `tests/` — unit tests

## How to contribute
- Use feature branches `feature/<name>`
- Follow code style (black, ruff)
- Open PRs with description, tests, and linked issue
