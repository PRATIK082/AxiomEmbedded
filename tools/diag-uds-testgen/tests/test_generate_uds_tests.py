"""Golden self-test: generator output is deterministic and complete (Rule 7.4)."""
from __future__ import annotations

import json
from pathlib import Path

from generate_uds_tests import run

HERE = Path(__file__).resolve().parent


def test_golden_matrix(tmp_path):
    out1 = tmp_path / "a"
    out2 = tmp_path / "b"
    p1 = run(HERE / "minimal_spec.yaml", out1)
    p2 = run(HERE / "minimal_spec.yaml", out2)
    # determinism: byte-identical trees
    h1 = sorted((p.relative_to(out1).as_posix(), p.read_bytes()) for p in out1.rglob("*") if p.is_file())
    h2 = sorted((p.relative_to(out2).as_posix(), p.read_bytes()) for p in out2.rglob("*") if p.is_file())
    assert [k for k, _ in h1] == [k for k, _ in h2]
    assert [b for _, b in h1] == [b for _, b in h2]
    # positive + negative emitted per service
    gen = out1 / "test" / "gen" / "DoorECU"
    assert (gen / "uds_10_diagnosticsessioncontrol.py").exists()
    assert (gen / "neg_10_diagnosticsessioncontrol.py").exists()
    assert (gen / "neg_11_ecureset.py").read_text().count("0x11") >= 1  # unsupported-SID NRC
    prov = json.loads((out1 / "evidence" / "gen" / "DoorECU" / "uds_provenance.json").read_text())
    assert prov["spec_sha256"] and prov["tool_version"] == "1.0.0"
    assert (out1 / "validation" / "gen" / "DoorECU" / "diag_acceptance.md").exists()
    assert len(p1["outputs"]) == len(p2["outputs"]) > 5
