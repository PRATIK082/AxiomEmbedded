# SPDX-License-Identifier: Apache-2.0
"""Tests for deterministic project detection + auto engagement."""

import pathlib

from packages import axiom_sdk
from packages.project_detect import detect_project


def _mk(tmp_path, files: dict) -> str:
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return str(tmp_path)


def test_detect_automotive(tmp_path):
    d = detect_project(_mk(tmp_path, {"net/can.dbc": "x", "ecu/swc.arxml": "x"}))
    assert d["status"] == "ok"
    assert d["domain"] == "automotive"
    assert d["confidence"] > 0.5
    assert d["signal_count"] >= 2


def test_detect_robotics_ros2(tmp_path):
    d = detect_project(_mk(tmp_path, {
        "src/pkg/package.xml": "<pkg/>",
        "CMakeLists.txt": "find_package(ament_cmake REQUIRED)\nfind_package(rclcpp REQUIRED)",
    }))
    assert d["domain"] == "robotics"
    assert d["platform"] == "ros2"


def test_detect_bare_metal(tmp_path):
    d = detect_project(_mk(tmp_path, {"fw/main.c": "int main(void){}", "fw/chip.ld": "MEMORY{}"}))
    assert d["platform"] == "mcu"
    assert d["os"] == "bare-metal"


def test_detect_missing_dir():
    d = detect_project("no-such-dir-xyz")
    assert d["status"] == "error"


def test_engage_auto_end_to_end(tmp_path):
    path = _mk(tmp_path, {"net/can.dbc": "x"})
    rep = axiom_sdk.engage_auto(path)
    assert rep["mode"] == "auto"
    assert rep["detection"]["domain"] == "automotive"
    assert rep["domain"] == "automotive"
    assert rep["skill_count"] > 0
    assert any("SKILL.md" in c for c in rep["context_files"])


def test_mcp_engage_auto_path(tmp_path):
    from axiom_mcp.server import dispatch

    path = _mk(tmp_path, {"src/pkg/package.xml": "<pkg/>"})
    res = dispatch("tools/call", {"name": "engage", "arguments": {"auto_path": path}})
    assert res["mode"] == "auto"
    assert res["detection"]["domain"] == "robotics"
