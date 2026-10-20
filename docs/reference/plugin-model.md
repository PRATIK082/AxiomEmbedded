# Plugin model

Every extension should declare:

- stable id/version
- capabilities
- dependencies
- inputs/outputs
- permissions
- supported domains/platforms
- verification expectations
- evidence hooks

Core packages must not import domain plugins directly.

## Extension points

| Point | Location | What you add |
| --- | --- | --- |
| Tool adapter | `tools/<id>/manifest.yaml` | A deterministic operation an agent can invoke |
| Tool facets | `registries/tool-facets.yaml` | The domain/platform/standard selection keys for a tool |
| Skill | `skills/<id>/` | A governed procedure (`SKILL.md` + manifests) |
| Agent | `agents/<id>/` | A role bound to skills, with permissions and approval gates |
| Domain / platform overlay | `domains/<id>/`, `platforms/<id>/` | Domain knowledge, controls and checklists |
| Rule / profile | `rules/`, `profiles/` | Applicable controls, tailoring and applicability metadata |

Selection is facet-driven: a tool engages when `"all"` is in its facets or the
requested value is listed. `axiom packs` resolves the tool/pip/agent set for a
request; `axiom tools` lists the surveyed open-source candidates that could
serve the same request (see `registries/tool-candidates.yaml`).

## Adapter classes

Not every upstream tool is a Python package. A tool manifest declares how the
tool is acquired, and the bridge is written against that contract.

| Class | `channel` | Manifest evidence | Example |
| --- | --- | --- | --- |
| Python package | `pip` | `dependencies:` holds a pip requirement; `external.entry_point` | `odxtools`, `udsoncan`, `gcovr` |
| Standalone binary | `binary` / `apt` | `entry_point` names the CLI; `source` is the upstream release | `clang-tidy`, `openocd`, `reviewdog` |
| Container image | `container` | `dependencies:` holds an image reference | `naivesystems/analyze`, `oss-review-toolkit` |
| Source tree | `source` | `source` is the upstream repo; build is out of band | `zephyr`, `mcuboot`, `fibexconverter` |

A bridge must:

1. fail closed with an actionable message when the tool is missing
   (`pip install <pack>`, `apt install <pkg>`, `docker pull <image>`);
2. never parse a format the upstream tool owns — validate shape only;
3. record provenance (upstream id/version, input hash) in its output;
4. be covered by a deterministic test that stubs the upstream tool.

## Licence policy

- Permissive (MIT/Apache-2.0/BSD) — import or subprocess, either is fine.
- Weak copyleft (LGPL/MPL/EPL) — import is acceptable; record the licence.
- Strong copyleft (GPL/AGPL) — `linkage: subprocess` **only**. Never link
  GPL/AGPL code into Axiom packages or bridge modules. An AGPL tool exposed
  as a network service additionally triggers source-offer obligations, so
  prefer permissive alternatives where the capability is equivalent.
- The registry validator enforces this: a copyleft candidate with
  `linkage: import` fails `python scripts/validate_tool_candidates.py`.

## Standards content policy

Standards metadata and applicability are stored; proprietary normative text
is not. A compliance artifact carries identifiers, applicability predicates,
project-authored interpretation and evidence references — never the licensed
prose of a standard.

Consequences for adapters:

- MISRA/CERT checkers report **rule identifiers**, not rule text. The rule
  text is supplied by the user at run time and is never vendored.
- CIS/OpenSCAP-style benchmark content is separately licensed and stays
  outside the repository.
- Machine-checkable applicability is expressed as data (for example OPA/Rego
  policies over `standard_id + clause_id + applicability`), so a rule can be
  enforced without the standard text ever entering the tree.
- No tool may claim certification or standards compliance from a heuristic
  check; the adapter reports findings, the human gate decides.
