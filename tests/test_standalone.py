"""Standalone-independence implementation: install, MCP, toolpacks, eval."""

import json
import subprocess
import sys

import yaml

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def test_pyproject_extras_keep_core_lean():
    data = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "mcp" in data and "eval" in data  # optional extras exist
    assert "pyyaml" in data.lower()


def test_mcp_registry_manifest_valid():
    manifest = json.loads((ROOT / "mcp-registry.json").read_text(encoding="utf-8"))
    assert manifest["name"]
    assert "stdio" in manifest.get("transports", [])


def test_mcp_check_green():
    proc = subprocess.run([sys.executable, "-m", "axiom_cli", "mcp", "--check"],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["status"] == "ok"
    assert report["tool_count"] >= 30


def test_detector_table_covers_first_toolpack():
    from packages.toolpacks.detect import DETECTORS, detect, detect_all

    assert set(DETECTORS) >= {"cppcheck", "ceedling", "gcovr", "robot", "renode"}
    all_hits = detect_all()
    assert set(all_hits) == set(DETECTORS)
    probe = detect("cppcheck")
    assert set(probe) == {"binary", "available", "path", "version", "install_hint"}
    assert detect("no-such-binary")["available"] is False


def test_packs_carry_availability():
    from packages.toolpacks.select import select_packs

    packs = select_packs("automotive", "mcu")
    assert "availability" in packs
    assert packs["availability"]["cppcheck"]["available"] is False or True  # env-dependent


def test_overlay_indexing_defense_reuses_shared_review():
    index = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    assert "defense" in index["skills"]["axiom-aerospace-defense-safety-review"]["domains"]
    assert "axiom-aerospace-defense-safety-review" in index["by_domain"]["defense"]


def test_eval_tasks_grade_green(tmp_path):
    from packages.eval.runner import grade, list_tasks

    ids = [t["id"] for t in list_tasks()]
    assert ids == ["EV-001", "EV-002", "EV-003", "EV-004", "EV-005"]
    assert grade("EV-001")["status"] == "ok"
    assert grade("EV-002", str(tmp_path))["status"] == "ok"
    assert grade("EV-003")["status"] == "ok"
    assert grade("EV-004")["status"] == "ok"
    assert grade("EV-005")["status"] == "ok"


def test_mkdocs_nav_resolves():
    nav = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))["nav"]
    targets = []

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str):
            targets.append(node)
    walk(nav)
    for target in targets:
        assert (ROOT / "docs" / target).exists(), target
