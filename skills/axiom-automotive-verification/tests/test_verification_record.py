"""Tests for the verification verdict record validator (file-path loaded)."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "verify_validate", SKILL_DIR / "scripts" / "validate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()

GOOD = """verdict: VERIFIED
coverage:
  - requirement_id: REQ-001
    status: VERIFIED
    evidence: unit-test-report#TC-001 PASS
"""

BAD = """verdict: VERIFIED
coverage:
  - requirement_id: REQ-001
    status: BLOCKED
    evidence: rig unavailable
"""


class VerificationRecordTests(unittest.TestCase):
    def _write(self, text):
        tmp = tempfile.NamedTemporaryFile(
            "w", suffix=".yaml", delete=False, encoding="utf-8"
        )
        tmp.write(text)
        tmp.close()
        return tmp.name

    def test_valid_record_passes(self):
        self.assertEqual(VALIDATOR.validate_record(self._write(GOOD)), [])

    def test_blocked_row_fails_verified_verdict(self):
        errors = VALIDATOR.validate_record(self._write(BAD))
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
