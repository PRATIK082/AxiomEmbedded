# Standards map -- axiom-automotive-code-review

Source of truth for identifiers: `standards/registry.yaml`. This file records
which standards this skill references and what it takes from each. It contains
no normative text -- only identifiers, applicability notes, and pointers.

| Registry ID | Role in this skill |
|---|---|
| `misra-c` | Rule-level C compliance delegated to `axiom-misra-c-cpp-review`; this skill records tool, version, rule set, deviations |
| `autosar-cpp14` | C++ review baseline for AUTOSAR C++14 subsets (interface contracts, error handling) |
| `iso-26262` | Safety context only: ASIL scope comes from the project safety plan; work products support confirmation reviews, never replace them |
| `automotive-spice` | Process alignment: review records serve SWE.5/SWE.6 verification evidence |

Rules:
- Never reproduce normative clauses, tables, or rule text from these standards.
- Never assign an ASIL or claim ASPICE capability from a review record alone.
- If the project uses a newer edition than the registry entry, record the exact
  edition in the review record and note deviations from this map.
