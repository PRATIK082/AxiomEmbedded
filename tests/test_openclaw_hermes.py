# SPDX-License-Identifier: Apache-2.0
"""OpenClaw/Hermes integration stays honest: audit green, doc pinned to code."""
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "clients" / "OPENCLAW_HERMES.md"


def test_audit_script_passes():
    proc = subprocess.run(
        [sys.executable, "scripts/audit_client_compat.py"],
        capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "problems=0" in proc.stdout, proc.stdout


def test_doc_pins_real_server_command():
    sys.path.insert(0, str(ROOT))
    from packages.installer import mcp_command
    server, _ = mcp_command()
    text = DOC.read_text(encoding="utf-8")
    assert server["command"] in text
    assert " ".join(server["args"]) in text or server["args"][1] in text


def test_doc_declares_installer_pending():
    text = DOC.read_text(encoding="utf-8")
    assert "not yet cover" in text or "pending" in text.lower()
    assert "275/275" in text
