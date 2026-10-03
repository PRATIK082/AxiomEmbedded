# Evidence ledger

Every material automated engineering action should be representable as evidence.

```yaml
evidence:
  id: EVD-0001
  action: code-change
  agent: implementation
  inputs: [REQ-1, ISSUE-9]
  source_baseline: sha256:...
  outputs: [SRC-23, UT-44]
  verification:
    unit: passed
    static_analysis: passed
  approval:
    status: pending
```

Evidence records should make it possible to answer: **what changed, why, from which baseline, by what agent/tool, and how it was verified?**
