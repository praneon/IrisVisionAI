"""Pytest test harness for engine tests.

Keeps tests import-stable without relying on a repository-level pytest.ini.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is importable so `import engine` works from any cwd.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
