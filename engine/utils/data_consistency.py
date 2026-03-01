"""Dataset consistency validation helpers for v0.5 reproducibility gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET


REQUIRED_LABELS = {
    "pupil",
    "iris",
    "collarette",
    "scurf_rim",
    "contraction_furrows",
}


def validate_data_consistency(repo_root: str | Path) -> list[str]:
    """Validate split/metadata/annotation integrity.

    Returns a list of human-readable issues. Empty list means pass.
    """

    root = Path(repo_root).resolve()
    data_dir = root / "data"
    metadata_path = data_dir / "metadata" / "metadata.csv"
    split_dir = data_dir / "splits"
    summary_path = split_dir / "split_summary.json"
    annotations_xml_path = _resolve_annotations_path(data_dir)

    issues: list[str] = []

    required_files = {
        "metadata": metadata_path,
        "split_summary": summary_path,
        "train_subjects": split_dir / "train_subjects.txt",
        "val_subjects": split_dir / "val_subjects.txt",
        "test_subjects": split_dir / "test_subjects.txt",
        "annotations_xml": annotations_xml_path,
    }
    for name, path in required_files.items():
        if not path.exists():
            issues.append(f"Missing required file: {name} -> {path}")

    if issues:
        return issues

    train_subjects = _load_subjects(required_files["train_subjects"])
    val_subjects = _load_subjects(required_files["val_subjects"])
    test_subjects = _load_subjects(required_files["test_subjects"])

    if train_subjects & val_subjects:
        issues.append("Split leakage: train and val subjects overlap.")
    if train_subjects & test_subjects:
        issues.append("Split leakage: train and test subjects overlap.")
    if val_subjects & test_subjects:
        issues.append("Split leakage: val and test subjects overlap.")

    split_subjects = {
        "train": train_subjects,
        "val": val_subjects,
        "test": test_subjects,
    }

    with metadata_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = set(reader.fieldnames or [])

    required_columns = {"image_id", "subject_id", "split"}
    missing_columns = sorted(required_columns - columns)
    if missing_columns:
        issues.append(f"metadata.csv missing required columns: {missing_columns}")
        return issues

    row_subjects: set[str] = set()
    split_counts = {"train": 0, "val": 0, "test": 0}

    for idx, row in enumerate(rows, start=2):
        subject = str(row.get("subject_id", "")).strip()
        split = str(row.get("split", "")).strip()
        if not subject:
            issues.append(f"metadata.csv line {idx}: empty subject_id")
            continue
        if split not in split_subjects:
            issues.append(f"metadata.csv line {idx}: invalid split '{split}'")
            continue

        row_subjects.add(subject)
        split_counts[split] += 1

        if subject not in split_subjects[split]:
            issues.append(
                f"metadata.csv line {idx}: subject_id {subject} tagged '{split}' but not present in {split}_subjects.txt"
            )

    listed_subjects = set().union(train_subjects, val_subjects, test_subjects)
    if row_subjects != listed_subjects:
        only_metadata = sorted(row_subjects - listed_subjects)
        only_lists = sorted(listed_subjects - row_subjects)
        if only_metadata:
            issues.append(f"Subjects in metadata but missing in split lists: {only_metadata[:10]}")
        if only_lists:
            issues.append(f"Subjects in split lists but missing in metadata: {only_lists[:10]}")

    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)

    _check_summary_int(issues, summary, "train_subjects", len(train_subjects))
    _check_summary_int(issues, summary, "val_subjects", len(val_subjects))
    _check_summary_int(issues, summary, "test_subjects", len(test_subjects))
    _check_summary_int(issues, summary, "total_subjects", len(listed_subjects))
    _check_summary_int(issues, summary, "train_images", split_counts["train"])
    _check_summary_int(issues, summary, "val_images", split_counts["val"])
    _check_summary_int(issues, summary, "test_images", split_counts["test"])
    _check_summary_int(issues, summary, "total_images", len(rows))

    issues.extend(_validate_annotation_labels(annotations_xml_path))

    return issues


def _resolve_annotations_path(data_dir: Path) -> Path:
    candidates = [
        data_dir / "annotations" / "pilot_v0_4" / "cvat_export" / "annotations.xml",
        data_dir / "annotations" / "v0_4_pilot" / "cvat_export" / "annotations.xml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Default to canonical legacy path for stable error messaging.
    return candidates[0]


def _load_subjects(path: Path) -> set[str]:
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def _check_summary_int(issues: list[str], summary: dict, key: str, expected: int) -> None:
    try:
        got = int(summary.get(key))
    except Exception:
        issues.append(f"split_summary.json key '{key}' is missing or not an integer")
        return
    if got != expected:
        issues.append(f"split_summary.json key '{key}' mismatch: expected {expected}, got {got}")


def _validate_annotation_labels(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except Exception as exc:
        return [f"Failed to parse annotations XML: {exc}"]

    labels = {elem.text.strip() for elem in root.findall("./meta/job/labels/label/name") if elem.text}
    if not labels:
        issues.append("annotations.xml contains no labels")
        return issues

    missing = REQUIRED_LABELS - labels
    unexpected = labels - REQUIRED_LABELS
    if missing:
        issues.append(f"annotations.xml missing required labels: {sorted(missing)}")
    if unexpected:
        issues.append(f"annotations.xml has unexpected labels: {sorted(unexpected)}")

    image_nodes = root.findall("./image")
    if not image_nodes:
        issues.append("annotations.xml contains no <image> entries")

    return issues
