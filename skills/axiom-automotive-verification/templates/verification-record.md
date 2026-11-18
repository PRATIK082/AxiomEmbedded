# Verification verdict record

Fill one row per in-scope requirement. This record is validated by
scripts/validate.py. Allowed status values: VERIFIED, FAILED, BLOCKED,
WAIVED, NOT_APPLICABLE.

verdict: PARTIAL
baseline_ref: REQ-BASELINE-<id>
method_summary: test + analysis + review per verification plan

coverage:
  - requirement_id: REQ-001
    status: VERIFIED
    evidence: unit-test-report#TC-001 PASS
  - requirement_id: REQ-002
    status: BLOCKED
    evidence: HIL rig unavailable until <date>; owner <name>
  - requirement_id: REQ-003
    status: WAIVED
    evidence: justification <text>; approval <reference>

waivers:
  - requirement_id: REQ-003
    justification: TODO
    approval_ref: TODO

independence:
  safety_related_verified_by: TODO (must differ per safety plan)

assumptions:
  - text: TODO
    owner: TODO
    expiry: TODO
