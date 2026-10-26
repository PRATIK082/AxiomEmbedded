"""Toolchain wrapper tests (deterministic, no toolchain required)."""
from packages.toolchain.build import parse_diagnostics
from packages.toolchain.detect import TOOLCHAINS, detect


def test_parse_diagnostics_gcc():
    text = "main.c:10:5: error: undeclared identifier\nfoo.c:2:1: warning: unused\n"
    ds = parse_diagnostics(text)
    assert len(ds) == 2
    assert ds[0]["severity"] == "error" and ds[0]["line"] == 10
    assert ds[1]["severity"] == "warning"


def test_detect_missing_tool():
    d = detect("definitely-not-a-tool-xyz")
    assert d["available"] is False
    assert d["path"] is None


def test_toolchains_has_compilers():
    assert "cmake" in TOOLCHAINS
    assert "arm-none-eabi-gcc" in TOOLCHAINS
