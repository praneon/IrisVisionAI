# CI Suggestions (GitHub Actions)

Suggested workflows:
- `lint-and-test.yml` — run black, ruff, and unit tests on PRs.
- `docker-build.yml` — build Docker image on `main`.
- `smoke-train.yml` — optional: run a short 1-epoch smoke training on small sample to validate pipeline.

Include secrets for W&B if used, and do NOT store model weights in repo.
