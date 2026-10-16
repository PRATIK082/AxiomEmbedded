# SPDX-License-Identifier: Apache-2.0
"""Generate gitignored client mirrors on demand before the test session.

.opencode/{agents,skills,commands,plugins}, .claude/ and .claude-plugin/
are build outputs of scripts/sync_clients.py (untracked by git). Tests
that read them regenerate first so a fresh clone needs no manual step.
"""

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def _generated_client_mirrors():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_clients.py")],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
