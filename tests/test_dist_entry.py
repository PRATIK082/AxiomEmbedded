# SPDX-License-Identifier: Apache-2.0
"""Phase 1a: distribution entry points — version flag and doctor checks."""

import json
import pathlib
import subprocess
import sys

from axiom_cli import __version__ as CLI_VERSION
from axiom_cli.main import get_version


def test_get_version_matches_source_tree():
    assert get_version() == CLI_VERSION != ""


def test_version_subcommand_prints_version():
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "version"],
        capture_output=True, text=True, check=True,
    )
    assert out.stdout.strip() == CLI_VERSION


def test_top_level_version_flag():
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "--version"],
        capture_output=True, text=True, check=True,
    )
    assert out.stdout.strip() == CLI_VERSION


def test_doctor_skip_tests_reports_expected_keys():
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "doctor", "--skip-tests"],
        capture_output=True, text=True, check=True,
    )
    assert "AxiomEmbedded doctor" in out.stdout
    for key in ("python", "axiom", "pyyaml", "axiom_on_path", "repo", "tests"):
        assert f"- {key}:" in out.stdout


def test_doctor_skip_tests_exits_zero_in_source_checkout():
    proc = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "doctor", "--skip-tests"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_repo_validate_passes_in_source_checkout():
    proc = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "repo", "validate"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS" in proc.stdout


def test_mcp_client_config_has_no_absolute_cwd():
    import pathlib

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    data = json.loads((ROOT / "clients" / "mcp.json").read_text(encoding="utf-8"))
    entry = data["mcpServers"]["axiom-embedded"]
    assert entry["args"] == ["-m", "axiom_cli", "mcp"]
    assert "cwd" not in entry, "absolute cwd breaks portability; set cwd at install time"


def test_wheel_builds_and_manifest_lists_content(tmp_path):
    """pip wheel builds into an isolated dir; MANIFEST.in grafts content trees."""
    root = pathlib.Path(__file__).resolve().parents[1]
    build = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", ".", "--no-deps",
         "-w", str(tmp_path)],
        capture_output=True, text=True, check=False,
        cwd=str(root),
    )
    assert build.returncode == 0, build.stderr[-2000:]
    assert list(tmp_path.glob("axiom_embedded-*.whl")), "wheel not built"
    manifest = (root / "MANIFEST.in").read_text(encoding="utf-8")
    for tree in ("skills", "agents", "registries", "schemas", "profiles",
                 "workflows", "domains", "platforms", "configs", "clients"):
        assert f"graft {tree}" in manifest, tree
        assert (root / tree).is_dir(), tree
