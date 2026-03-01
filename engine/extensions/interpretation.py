"""Structural interpretation extension (non-diagnostic explanatory text)."""

from __future__ import annotations

import re
from typing import Any

from engine.app.analysis_types import ExtensionContext, ExtensionResult, ExtensionStatus


DISCLAIMER_HEADER = (
    "DISCLAIMER: Research-only structural analysis. This output is not medical advice, "
    "not a diagnosis, and must not be used for clinical decisions."
)

BANNED_TERMS = {
    "diagnosis",
    "disease",
    "syndrome",
    "treatment",
    "cure",
    "clinical",
    "prognosis",
    "risk score",
    "medical condition",
}


class InterpretationExtension:
    """Create deterministic structural summaries and optional VLM explanation."""

    name = "interpretation"
    version = "1"
    requires: list[str] = []
    optional_requires: list[str] = ["micro_features", "sector_mapping"]

    def run(self, context: ExtensionContext) -> ExtensionResult:
        cfg = context.config.get("extensions", {}).get(self.name, {})
        mode = str(cfg.get("mode", "deterministic_only")).strip()
        if mode == "disabled":
            return ExtensionResult(status=ExtensionStatus.SKIPPED, warning="Interpretation disabled by config.")

        summary = self._build_structured_summary(context)
        explanation = self._build_deterministic_text(summary)

        warnings: list[str] = []
        if mode == "vlm_enabled":
            # Placeholder augmentation hook to keep deterministic facts authoritative.
            extra = str(cfg.get("vlm_note", "")).strip()
            if extra:
                explanation += f"\n\nAdditional note: {extra}"
            else:
                warnings.append("VLM mode enabled but no provider configured; deterministic text used.")

        safe_text, removed = self._sanitize(explanation)
        if removed:
            warnings.append("Interpretation text sanitized due to banned vocabulary.")

        payload: dict[str, Any] = {
            "interpretation_summary": summary,
            "interpretation_text": f"{DISCLAIMER_HEADER}\n\n{safe_text}".strip(),
            "safety_events": [
                {
                    "event": "banned_vocabulary_filtered",
                    "count": len(removed),
                    "terms": sorted(set(removed)),
                }
            ]
            if removed
            else [],
        }
        return ExtensionResult(
            status=ExtensionStatus.SUCCESS,
            payload=payload,
            warning="; ".join(warnings) if warnings else None,
        )

    def _build_structured_summary(self, context: ExtensionContext) -> dict[str, Any]:
        metrics = context.metrics
        micro = context.extension_outputs.get("micro_features", {}).get("micro_feature_metrics", {})

        return {
            "ratios": {
                "pupil_to_iris": float(metrics.get("pupil_to_iris", 0.0)),
                "collarette_to_iris": float(metrics.get("collarette_to_iris", 0.0)),
                "furrow_to_iris": float(metrics.get("furrow_to_iris", 0.0)),
                "scurf_to_iris": float(metrics.get("scurf_to_iris", 0.0)),
            },
            "micro_features": {
                "lacunae_count": int(micro.get("lacunae_count", 0)),
                "crypt_count": int(micro.get("crypt_count", 0)),
                "area_ratio": float(micro.get("area_ratio", 0.0)),
            },
            "notes": [
                "Structural-only description generated from segmentation and extension metrics.",
                "No diagnostic interpretation is performed.",
            ],
        }

    def _build_deterministic_text(self, summary: dict[str, Any]) -> str:
        ratios = summary["ratios"]
        micro = summary["micro_features"]
        lines = [
            "Deterministic structural summary:",
            f"- Pupil/Iris ratio: {ratios['pupil_to_iris']:.4f}",
            f"- Collarette/Iris ratio: {ratios['collarette_to_iris']:.4f}",
            f"- Furrow/Iris ratio: {ratios['furrow_to_iris']:.4f}",
            f"- Scurf/Iris ratio: {ratios['scurf_to_iris']:.4f}",
            f"- Lacunae count: {micro['lacunae_count']}",
            f"- Crypt count: {micro['crypt_count']}",
            f"- Micro-feature area ratio: {micro['area_ratio']:.4f}",
        ]
        return "\n".join(lines)

    def _sanitize(self, text: str) -> tuple[str, list[str]]:
        removed_terms: list[str] = []
        kept_sentences: list[str] = []

        sentences = re.split(r"(?<=[.!?])\s+|\n", text)
        for sentence in sentences:
            if not sentence.strip():
                continue
            lower = sentence.lower()
            hit_terms = [term for term in BANNED_TERMS if term in lower]
            if hit_terms:
                removed_terms.extend(hit_terms)
                continue
            kept_sentences.append(sentence.strip())

        safe = "\n".join(kept_sentences).strip()
        if not safe:
            safe = "No explanatory text available after safety filtering."
        return safe, removed_terms
