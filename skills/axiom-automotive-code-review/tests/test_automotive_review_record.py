"""Tests for the axiom-automotive-code-review record validator."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATE = SKILL_DIR / "scripts" / "validate.py"

GOOD = textwrap.dedent("""\
    review:
      id: REV-0001
      date: 2026-11-16
      scope: {repository: /repo, files: [src/canif.c]}
      module: {id: CanIf, autosar_release: R25-11, asil_scope: B}
      standard: {coding: 'MISRA C:2025', deviations: []}
      reviewers: [{name: A. Peer, role: peer}, {name: B. Author, role: author}]
      sampling: full
      rule_check: {tool: qac-9.7, ruleset: misra-c-2025, unresolved_mandatory: 0}
      defects:
        - {id: D-1, location: 'canif.c:CanIf_Init', severity: ADVISORY,
           requirement: SWRS-001, status: waived}
      verdict: READY
      evidence: [build/test-results.json]
    """)

BAD_READY_WITH_BLOCKED = GOOD.replace("verdict: READY", "verdict: READY").replace(
    "severity: ADVISORY", "severity: BLOCKED").replace("status: waived", "status: open")


def _run(record_text: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "record.yaml"
        path.write_text(record_text, encoding="utf-8")
        return subprocess.run([sys.executable, str(VALIDATE), str(path)],
                              capture_output=True, text=True)


def test_accepts_valid_record():
    proc = _run(GOOD)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_rejects_ready_with_open_blocked():
    proc = _run(BAD_READY_WITH_BLOCKED)
    assert proc.returncode == 1
    assert "BLOCKED" in proc.stdout
