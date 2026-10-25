"""Embedded toolchain wrappers (build/flash/test)."""
from packages.toolchain.detect import detect, detect_all, available_toolchains, TOOLCHAINS
from packages.toolchain.build import run_build, cmake_configure, cmake_build, make_build, parse_diagnostics
from packages.toolchain.test import run_tests, run_pytest, run_ceedling
from packages.toolchain.coverage import run_coverage
from packages.toolchain.static import run_static
from packages.toolchain.serial import capture_serial
from packages.toolchain.flash import flash

__all__ = ["detect", "detect_all", "available_toolchains", "TOOLCHAINS",
           "run_build", "cmake_configure", "cmake_build", "make_build",
           "parse_diagnostics", "run_tests", "run_pytest", "run_ceedling",
           "run_coverage", "run_static", "capture_serial", "flash"]
