"""Tests for the axiom-aerospace-requirements-allocation record validator."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "allocation_validate", SKILL_DIR / "scripts" / "validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

GOOD = """| System requirement | Allocated item | Owner | Interface contract | Status | Rationale / risk / approval |
| SYS-REQ-001 | SW-ITEM-1 | J. Doe | ICD-5 | ALLOCATED | normal allocation |
| SYS-REQ-002 | N/A | N/A | N/A | UNALLOCATED | cannot allocate; low risk; approved by J. Doe |
- Baseline count: 2
- ALLOCATED count: 1
- UNALLOCATED count: 1
"""

BAD = """| System requirement | Allocated item | Owner | Interface contract | Status | Rationale / risk / approval |
| SYS-REQ-001 | N/A | N/A | N/A | ALLOCATED | missing owner |
- Baseline count: 3
- ALLOCATED count: 1
- UNALLOCATED count: 1
"""


class AllocationRecordTests(unittest.TestCase):
    def test_valid_record_passes(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.md"
            path.write_text(GOOD, encoding="utf-8")
            self.assertEqual(MODULE.validate_record(path), [])

    def test_invalid_record_fails(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.md"
            path.write_text(BAD, encoding="utf-8")
            errors = MODULE.validate_record(path)
            self.assertTrue(any("owner" in error for error in errors))
            self.assertTrue(any("reconcile" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
