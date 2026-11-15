# SPDX-License-Identifier: Apache-2.0
"""Packaging parity: VERSION, pyproject, npm wrapper, and CLI agree."""

import json
import pathlib

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

try:
    from axiom_cli import __version__ as CLI_VERSION
except Exception:
    CLI_VERSION = None


def _version_file() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_version_file_matches_pyproject():
    data = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{_version_file()}"' in data


def test_package_json_parses_and_matches_version():
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["name"] == "axiom-embedded"
    assert pkg["version"] == _version_file()
    assert pkg["bin"]["axiom"] == "bin/axiom.js"
    assert (ROOT / pkg["bin"]["axiom"]).exists()
    assert pkg["license"] == "Apache-2.0"


def test_cli_version_matches_version_file():
    assert CLI_VERSION is not None
    assert CLI_VERSION == _version_file()


def test_manifest_grafts_content_trees():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    for tree in ("skills", "agents", "registries", "schemas", "profiles",
                 "workflows", "domains", "platforms", "configs", "clients"):
        assert f"graft {tree}" in manifest, tree
        assert (ROOT / tree).is_dir(), tree


def test_new_readiness_skills_registered():
    data = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    ids = {s["id"] for s in data["skills"]}
    assert "axiom-production-readiness" in ids
    assert "axiom-deployment-readiness" in ids
    assert len(data["skills"]) >= 261


@pytest.mark.skipif(CLI_VERSION is None, reason="axiom_cli not importable")
def test_shim_files_present():
    assert (ROOT / "bin" / "axiom.js").exists()
    assert (ROOT / "bin" / "postinstall.js").exists()
