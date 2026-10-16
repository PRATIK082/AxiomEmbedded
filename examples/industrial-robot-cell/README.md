# Industrial robot cell — end-to-end assurance example

Small pick-and-place cell: 6-axis arm, fence with gate interlock, PLC safety
controller, HMI panel, cell Wi-Fi gateway. Demonstrates the five assurance
artifacts plus independent reviews and hazard→control→verification trace.

## Run

```bash
python -m axiom_cli artifact validate examples/industrial-robot-cell/artifacts/scope.yaml
python -m axiom_cli artifact validate examples/industrial-robot-cell/artifacts/hazard-risk.yaml
python -m axiom_cli artifact validate examples/industrial-robot-cell/artifacts/safety-requirements.yaml
python -m axiom_cli artifact validate examples/industrial-robot-cell/artifacts/vnv-plan.yaml
python -m axiom_cli artifact validate examples/industrial-robot-cell/artifacts/threat-model.yaml
python -m axiom_cli trace check examples/industrial-robot-cell/artifacts
python scripts/validate_skills.py --skill axiom-scope-context
python -m pytest -q tests/test_assurance.py
```

## Chain

scope (SCOPE-CELL-01) → hazards (HAZ-001..004) → requirements (REQ-001..005)
→ tests (TEST-001..005) → threats (SEC-001..002); reviews REV-* per artifact.

All output is draft engineering evidence and requires qualified human review.
It is not a certification or conformity approval.
