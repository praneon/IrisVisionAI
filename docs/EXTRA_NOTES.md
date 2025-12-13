# Extra Notes & Edge Cases

- Occlusions: Mask or exclude images with heavy eyelid/eyelash occlusion.
- Artifacts: Mark specular highlights as `artifact` to avoid training noise.
- SAM proposals: store raw SAM outputs in `tmp/sam_proposals/` for audit.
- Inter-annotator log: maintain `docs/annotations_agreement.csv`.
- Backup: periodically backup `data/working/` and `annotations/` externally.
