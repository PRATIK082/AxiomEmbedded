"""Tests for the applicability matrix validator."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"
_spec = importlib.util.spec_from_file_location("applicability_validate", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
validate_matrix = _mod.validate_matrix

GOOD = """| iso-26262 | 2018 | APPLICABLE | SafetyPlan v1 | Safety scope governs ECU X |
| misra-c | 2012 | NOT_APPLICABLE | | Project uses C++ only |
| unece-r155 | | DEFERRED | Type approval TBD | Owner: J. Doe |
"""

BAD = """| iso-26262 | 2018 | MAYBE | SafetyPlan v1 | Safety scope governs ECU X |
| misra-c | 2012 | APPLICABLE | | No governor named |
| iso-sae-21434 | 2021 | NOT_APPLICABLE | | |
"""


class ValidateMatrixTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def test_good_matrix_passes(self) -> None:
        self.assertEqual(validate_matrix(self._write(GOOD)), [])

    def test_bad_matrix_fails(self) -> None:
        errors = validate_matrix(self._write(BAD))
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
