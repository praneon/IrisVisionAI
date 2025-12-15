# Reproducibility Checklist

- Fix random seeds for `random`, `numpy`, `torch`.
- Set `torch.backends.cudnn.deterministic=True` where applicable.
- Save full `requirements.txt` and `environment.yml`.
- Provide Dockerfile for reproducible environment.
- Save `experiments/*.yaml` config for every run.
- Log artifacts to W&B or local `experiments/exp-*/checkpoints/`.
- Keep original raw images untouched; work only on `data/working/`.
