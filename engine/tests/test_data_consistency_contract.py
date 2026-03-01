from __future__ import annotations

import csv
import json
from pathlib import Path

from engine.utils.data_consistency import validate_data_consistency


def _write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + "\n", encoding="utf-8")


def _build_min_repo(root: Path) -> None:
    data = root / "data"
    (data / "metadata").mkdir(parents=True, exist_ok=True)
    (data / "splits").mkdir(parents=True, exist_ok=True)
    (data / "annotations" / "pilot_v0_4" / "cvat_export").mkdir(parents=True, exist_ok=True)

    with (data / "metadata" / "metadata.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image_id", "subject_id", "split"])
        writer.writeheader()
        writer.writerow({"image_id": "A", "subject_id": "1", "split": "train"})
        writer.writerow({"image_id": "B", "subject_id": "2", "split": "test"})

    _write_lines(data / "splits" / "train_subjects.txt", ["1"])
    _write_lines(data / "splits" / "val_subjects.txt", [])
    _write_lines(data / "splits" / "test_subjects.txt", ["2"])

    summary = {
        "seed": 69,
        "total_subjects": 2,
        "train_subjects": 1,
        "val_subjects": 0,
        "test_subjects": 1,
        "total_images": 2,
        "train_images": 1,
        "val_images": 0,
        "test_images": 1,
    }
    (data / "splits" / "split_summary.json").write_text(json.dumps(summary), encoding="utf-8")

    xml = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<annotations>
  <meta>
    <job>
      <labels>
        <label><name>pupil</name></label>
        <label><name>iris</name></label>
        <label><name>collarette</name></label>
        <label><name>scurf_rim</name></label>
        <label><name>contraction_furrows</name></label>
      </labels>
    </job>
  </meta>
  <image id=\"0\" name=\"A.jpg\" width=\"10\" height=\"10\" />
</annotations>
"""
    (data / "annotations" / "pilot_v0_4" / "cvat_export" / "annotations.xml").write_text(xml, encoding="utf-8")


def test_validate_data_consistency_pass(tmp_path: Path) -> None:
    _build_min_repo(tmp_path)
    issues = validate_data_consistency(tmp_path)
    assert issues == []


def test_validate_data_consistency_detects_overlap_and_summary_mismatch(tmp_path: Path) -> None:
    _build_min_repo(tmp_path)
    data = tmp_path / "data"

    _write_lines(data / "splits" / "val_subjects.txt", ["1"])
    (data / "splits" / "split_summary.json").write_text(
        json.dumps(
            {
                "seed": 69,
                "total_subjects": 2,
                "train_subjects": 1,
                "val_subjects": 1,
                "test_subjects": 1,
                "total_images": 2,
                "train_images": 99,
                "val_images": 0,
                "test_images": 1,
            }
        ),
        encoding="utf-8",
    )

    issues = validate_data_consistency(tmp_path)
    joined = "\n".join(issues)
    assert "Split leakage: train and val subjects overlap." in joined
    assert "train_images" in joined
