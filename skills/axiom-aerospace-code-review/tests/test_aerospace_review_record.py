"""Tests for the review record validator (file-path loading)."""
import importlib.util
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "review_validate", BASE / "scripts" / "validate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReviewRecordTests(unittest.TestCase):
    def test_template_placeholders_fail(self):
        errs = mod.validate_record(BASE / "templates" / "review-record.md")
        self.assertTrue(any("TODO" in e for e in errs))

    def test_minimal_valid_record_passes(self):
        import tempfile
        gates = "\n".join(f"  - {g}: pass" for g in mod.REQUIRED_GATES)
        rec = (
            "artifact: src/ctrl.c\nartifact_type: CODE\ndal: B\n"
            "reviewer: j.doe\nindependence_basis: separate team\n"
            f"gates:\n{gates}\nfindings: []\nverdict: PASS\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md",
                                         delete=False) as fh:
            fh.write(rec)
            name = fh.name
        self.assertEqual(mod.validate_record(name), [])


if __name__ == "__main__":
    unittest.main()
