# External packs: link, don't bundle

Policy for third-party / independently-developed pip packs and CLI agents
(e.g. ARXML/ODX/CDD/XLSX → internal-YAML diagnostic extractors, standard
script generators, auto bug-fix / code-review / code-update CLI agents).

## Decision

**Develop independent, map here.** Keep the external pack in its own
repository and release cycle (own versioning, own AUTOSAR-version support
matrix). In this repo, add only a thin **bridge**:

- `tools/<bridge>/` — declares the pip dependency + entry point, validates
  the pack's output against the canonical schema, records provenance.
- `agents/<mapping>/` — binds an external CLI agent to one or more Axiom
  skills, with permissions and approval gates.

Rationale: bundling copies would freeze AUTOSAR-version support at merge
time, duplicate licensing surface, and break the manifest-driven plugin
strategy (`configs/project.yaml`: `plugin_strategy: manifest-driven`).
Bridges keep this repo as the integration contract while packs evolve
independently.

## Mapping recipe (normative for new bridges)

### 1. External pack requirements

The pack MUST expose:

1. A pip-installable distribution with pinned versions
   (e.g. `acme-diag-extract>=2.1,<3`).
2. A stable Python entry point or CLI
   (e.g. `acme_diag_extract.extract(in_path) -> dict`
   or `acme-diag-extract <in> --out spec.yaml`).
3. Output conforming to the canonical schema
   (`schemas/uds-test-spec.schema.json` for diag extracts).
   The pack owns format knowledge (all ARXML types, all AUTOSAR versions);
   the bridge owns contract validation, never parsing.

### 2. Bridge tool (`tools/<bridge>/`)

Required files:

| File | Content |
| ---- | ------- |
| `manifest.yaml` | `id`, `version`, `purpose` per `schemas/tool.schema.json`, plus `external:` (pip spec, entry_point, supported pack versions) and `dependencies:` (pip install string) |
| `README.md` | Pack source, install command, supported input formats/versions |
| `bridge.py` | Import-by-entry-point shim: clear error when pack missing; pass-through call; minimal schema-shape validation; provenance record |
| `tests/test_bridge.py` | Contract test with a stubbed pack module (no real dependency in CI) |

The bridge MUST fail closed with an actionable message when the pack is
not installed (`pip install <pack>`), and MUST reject out-of-matrix output
with element/row locations — never silently coerce.

### 3. Agent mapping (`agents/<mapping>/`)

Required files: `manifest.json` (per `schemas/agent.schema.json`:
`id`, `version`, `purpose`, `permissions`), `AGENT.md` (operating contract:
which skills it must load first, what the external CLI may/may not do,
approval gates). Register in `registries/agents.json`.

External CLI agents that modify code (auto bug-fix / update) MUST:

- Declare `filesystem: write` (or `read` for review-only) and
  `git_push: false`, `release: false` in the manifest.
- Load the governing skill(s) before invoking the CLI
  (e.g. `automotive-diagnostics` Rules 1–2 for diag work).
- Set `approval.required_for_sensitive_change: true` so safety/security
  deltas stop at the human gate per `configs/project.yaml`.

### 4. Reference example

- Tool bridge: `tools/diag-extract-bridge/` (extract packs → canonical spec).
- Agent mapping: `agents/diag-auto-review/` (external review/fix CLI
  bound to `automotive-diagnostics` + `code-review`).

Future AI: copy these two directories as the template for any new
external pack or CLI agent. Same shape, new `id`.
