# Context policy

The context engine uses a layered strategy:

```text
Task → artifact roots → dependency/traceability graph → focused files → applicable rules/tests → recent changes
```

A full-repository read is an exception and must be justified. Generated artifacts, binaries, vendored trees and vendored/generated snapshots are excluded by default.

The goal is not a specific token number. The goal is **deterministic relevance with a bounded context budget**.
