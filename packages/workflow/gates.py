from dataclasses import dataclass

@dataclass(frozen=True)
class GateResult:
    id: str
    passed: bool
    reason: str

def evidence_gate(has_evidence: bool) -> GateResult:
    return GateResult("evidence-required", has_evidence, "evidence present" if has_evidence else "evidence missing")
