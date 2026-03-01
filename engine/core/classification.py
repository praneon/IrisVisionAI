"""Rule-based deterministic phenotype classification."""

from __future__ import annotations

from typing import Any, Dict, List



def classify_phenotype(ratios: Dict[str, float], rules_config: Dict[str, Any]) -> List[str]:
    """Evaluate threshold rules from JSON configuration in listed order."""
    labels: List[str] = []
    for rule in rules_config.get("rules", []):
        metric = rule["metric"]
        operator = rule.get("operator", ">")
        threshold = float(rule["threshold"])
        label = rule["label"]

        value = float(ratios[metric])
        passed = (value > threshold) if operator == ">" else (value >= threshold)
        if passed:
            labels.append(label)
    return labels
