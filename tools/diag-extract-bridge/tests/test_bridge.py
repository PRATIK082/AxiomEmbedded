"""Contract tests for the extract bridge (stub pack, no real dependency)."""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bridge as shim


def _stub_pack(monkeypatch, payload):
    mod = types.ModuleType("acme_diag_extract")
    mod.extract = lambda in_path: payload
    monkeypatch.setitem(sys.modules, "acme_diag_extract", mod)


def test_bridge_passes_pack_output_through(tmp_path, monkeypatch):
    payload = {"ecu": {"name": "DoorECU"},
               "services": [{"sid": 0x22, "name": "ReadDataByIdentifier", "supported": True}]}
    _stub_pack(monkeypatch, payload)
    src = tmp_path / "in.arxml"
    src.write_text("<ARXML/>", encoding="utf-8")
    out = tmp_path / "spec.json"
    info = shim.run(src, out)
    assert json.loads(out.read_text(encoding="utf-8"))["ecu"]["name"] == "DoorECU"
    assert info["output_sha256"]


def test_bridge_rejects_bad_shape(tmp_path, monkeypatch):
    _stub_pack(monkeypatch, {"ecu": {"name": "X"}})
    src = tmp_path / "in.odx"
    src.write_text("<ODX/>", encoding="utf-8")
    with pytest.raises(SystemExit):
        shim.run(src, tmp_path / "spec.json")


def test_bridge_fails_closed_without_pack(tmp_path, monkeypatch):
    monkeypatch.delitem(sys.modules, "acme_diag_extract", raising=False)
    src = tmp_path / "in.arxml"
    src.write_text("<ARXML/>", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        shim.run(src, tmp_path / "spec.json")
    assert "pip install" in str(exc.value)
