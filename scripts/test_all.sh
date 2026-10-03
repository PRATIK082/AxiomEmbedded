#!/usr/bin/env bash
# Wrapper for local and CI verification of embedded-skills-deep-update.
set -euo pipefail
SKILL="${1:---all}"
if [ "$SKILL" = "--all" ]; then
  python -m compileall -q axiom_cli packages scripts
  python -m pytest -q
  python -m axiom_cli doctor
  python -m axiom_cli repo validate
  python scripts/audit_skills.py
else
  python scripts/verify_skill.py --skill "$SKILL"
fi
