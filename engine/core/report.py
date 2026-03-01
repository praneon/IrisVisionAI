"""Optional PDF report generator for IrisAtlasAI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



def create_pdf_report(
    original_path: str | Path,
    overlay_path: str | Path,
    output_pdf_path: str | Path,
    summary_json: Dict[str, Any],
) -> Path:
    """Create a simple deterministic PDF report."""
    out = Path(output_pdf_path)
    c = canvas.Canvas(str(out), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(36, height - 36, "IrisAtlasAI Structural Analysis Report")

    c.setFont("Helvetica", 10)
    c.drawString(36, height - 56, f"Input: {Path(original_path).name}")

    c.drawImage(str(original_path), 36, height - 310, width=240, height=240, preserveAspectRatio=True)
    c.drawImage(str(overlay_path), 300, height - 310, width=240, height=240, preserveAspectRatio=True)

    c.setFont("Helvetica", 9)
    json_text = json.dumps(summary_json, indent=2)
    y = height - 340
    for line in json_text.splitlines():
        c.drawString(36, y, line[:120])
        y -= 11
        if y < 36:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 36

    c.save()
    return out
