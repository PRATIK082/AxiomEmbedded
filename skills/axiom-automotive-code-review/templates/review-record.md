# Code review record -- template

Copy this file per review. All fields are required unless marked optional.
`scripts/validate.py` checks the required fields.

```yaml
review:
  id: REV-0001
  date: YYYY-MM-DD
  scope:
    repository: <path>
    files: [<path>, ...]        # or: change_set: <id>
  module:
    id: <module-id>
    autosar_release: <release>
    asil_scope: <QM|A|B|C|D>    # from the project safety plan, never assigned here
  standard:
    coding: <e.g. MISRA C:2025> # exact edition in force
    deviations: [<id>, ...]     # optional
  reviewers:
    - name: <name>
      role: author|peer|independent
  sampling: full|risk-based     # risk-based requires rationale below
  sampling_rationale: <text>    # required when sampling is risk-based
  rule_check:
    tool: <tool name and version>
    ruleset: <ruleset>
    unresolved_mandatory: 0
  defects:
    - id: D-1
      location: <file:function>
      severity: BLOCKED|REWORK|ADVISORY
      requirement: <requirement id or UNREVIEWED-waiver>
      status: open|fixed|waived
  verdict: READY|REWORK|BLOCKED
  evidence: [<path or reference>, ...]
```
