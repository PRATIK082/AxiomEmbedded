"""Exemplar script tests (run under pytest)."""
from __future__ import annotations
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "axiom-autosar-classic-bsw-integration" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "axiom-diagnostics-uds" / "scripts"))

import check_bsw  # noqa: E402
import check_uds_matrix  # noqa: E402


def test_bsw_full_config_passes():
    text = ("RTE OS COM PduR CanIf CanTp Dcm Dem NvM EcuM "
            "ports runnables events signals")
    assert check_bsw.check_config(text)["verdict"] == "PASS"


def test_bsw_missing_modules_review():
    res = check_bsw.check_config("RTE OS only ports")
    assert res["verdict"] == "REVIEW"
    assert "COM" in res["modules_missing"]


def test_uds_matrix_ok():
    spec = {"services": [
        {"sid": 0x10, "sessions": ["default"]},
        {"sid": 0x22, "sessions": ["extended"], "dids": [{"id": 0xF190}]},
        {"sid": 0x19, "sessions": ["default"], "subfunctions": [1]},
        {"sid": 0x27, "sessions": ["extended"]},
        {"sid": 0x3E, "sessions": ["default"]},
    ]}
    assert check_uds_matrix.check_matrix(spec) == []


def test_uds_matrix_missing_sid():
    assert any("0x10" in e for e in
               check_uds_matrix.check_matrix({"services": []}))
