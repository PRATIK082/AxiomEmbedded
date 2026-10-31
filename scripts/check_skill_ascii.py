"""ASCII cleanliness check for skill files.

Ensures every file under skills/ contains only ASCII characters, so generated
client mirrors and skill_pipeline --check never propagate mojibake or junk
glyphs into shipped artifacts.

Usage:
    python scripts/check_skill_ascii.py            # scan skills/
    python scripts/check_skill_ascii.py <path>     # scan a custom tree
Exit 0 if clean, 1 if any non-ASCII byte is found.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

TEXT_EXTS = {".md", ".yaml", ".yml", ".py", ".json", ".csv", ".txt",
             ".toml", ".cfg", ".ini", ".rst"}


def scan(root: pathlib.Path):
    findings = []
    if root.is_file():
        targets = [root]
    else:
        targets = [p for p in root.rglob("*") if p.is_file()]
    for p in targets:
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        if "__pycache__" in p.parts:
            continue
        try:
            data = p.read_bytes()
            text = data.decode("utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for ch in line:
                if ord(ch) > 127:
                    findings.append((p, lineno, repr(ch)))
                    break
    return findings


def main(argv=None):
    import argparse

    ap = argparse.ArgumentParser(description="Check skill files are ASCII-only.")
    ap.add_argument("path", nargs="?", default="skills")
    ns = ap.parse_args(argv)
    root = pathlib.Path(ns.path)
    if not root.is_absolute():
        root = ROOT / root
    findings = scan(root)
    if not findings:
        print("OK: %s is ASCII-clean" % root)
        return 0
    print("FAIL: %d non-ASCII line(s) in %s" % (len(findings), root))
    for p, ln, ch in findings[:50]:
        print("  %s:%d %s" % (p, ln, ch))
    if len(findings) > 50:
        print("  ... and %d more" % (len(findings) - 50))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
