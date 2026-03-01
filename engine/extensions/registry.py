"""Extension registry and execution order lock."""

from __future__ import annotations

from engine.app.analysis_types import ExtensionStatus
from engine.extensions.interpretation import InterpretationExtension
from engine.extensions.micro_features import MicroFeaturesExtension
from engine.extensions.sector_mapping import SectorMappingExtension


EXECUTION_ORDER = [
    "micro_features",
    "sector_mapping",
    "interpretation",
]

ALLOWED_EXTENSION_STATES = {
    ExtensionStatus.SUCCESS.value,
    ExtensionStatus.SKIPPED.value,
    ExtensionStatus.TIMEOUT.value,
    ExtensionStatus.FAILED.value,
}

_EXTENSION_FACTORIES = {
    "micro_features": MicroFeaturesExtension,
    "sector_mapping": SectorMappingExtension,
    "interpretation": InterpretationExtension,
}


def build_extensions() -> dict[str, object]:
    """Instantiate all known extensions by locked name."""

    return {name: _EXTENSION_FACTORIES[name]() for name in EXECUTION_ORDER}
