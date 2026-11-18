# SPDX-License-Identifier: Apache-2.0
"""Structural validator for axiom-bus-protocol-validation (stdlib only)."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def main() -> int:
    errors: list[str] = []
    skill = ROOT / "skills" / "axiom-bus-protocol-validation"
    for rel in ("SKILL.md", "manifest.yaml", "checklists/review.yaml",
                "references/overview.md", "templates/artifact.template.md",
                "tests/evals.json"):
        if not (skill / rel).exists():
            errors.append(f"missing {rel}")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    for token in ("CAN", "UART", "SPI", "I2C", "MQTT", "BLE",
                  "SW-to-HW", "HW-to-SW"):
        if token not in text:
            errors.append(f"SKILL.md missing token: {token}")
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"- {e}")
        return 1
    print("axiom-bus-protocol-validation structural check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
