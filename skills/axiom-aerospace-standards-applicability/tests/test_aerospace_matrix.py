"""Tests for the applicability matrix validator (file-path loading)."""
import importlib.util
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "applicability_validate", BASE / "scripts" / "validate.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class MatrixTests(unittest.TestCase):
    def test_template_fails(self):
        errors = mod.validate(BASE / "templates" / "applicability-matrix.md")
        self.assertTrue(errors, "template placeholders must fail validation")

    def test_valid_matrix_passes(self):
        sample = (
            "| Standard | Revision | Lifecycle | Verdict | Rationale |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| ARP4754A | A | published | APPLICABLE | system-level item |\n"
        )
        tmp = BASE / "tests" / "_tmp_matrix.md"
        try:
            tmp.write_text(
                "# Matrix\n\n" + sample,
                encoding="utf-8",
            )
            self.assertEqual(mod.validate(tmp), [])
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
