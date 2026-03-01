# Evaluation Protocol

This project evaluates segmentation, detection, and rule/mapping layers with transparent reporting.
The goal is to understand model behavior, not chase a single headline metric.

## 1. Segmentation

Report at least:
- Dice per class
- IoU per class and mean IoU
- precision/recall trends where useful

Also keep qualitative overlays for:
- strong cases
- weak cases
- typical cases

Each qualitative panel should compare prediction vs reference mask clearly.

## 2. Micro-feature detection

Report at least:
- AP@0.5
- AP@0.5:0.95
- class-level precision/recall
- small-object performance focus (for tiny structures)

Include failure analysis:
- false positives
- false negatives
- class confusion patterns

## 3. Sector mapping and interpretation layers

These are not pure ML prediction tasks, so evaluate them differently.

### Sector mapping
- deterministic test cases with known sector expectations
- boundary-condition checks
- regression tests for coordinate conversion

### Interpretation layer
- review for structural consistency
- verify non-diagnostic language policy
- ensure generated text matches actual structural inputs

## 4. Artifact policy

Each evaluation cycle should preserve:
- metric tables
- representative visual outputs
- notes on known failure modes

Avoid reporting a single score without context.
