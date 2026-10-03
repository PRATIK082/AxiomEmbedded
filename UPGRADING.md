# Upgrading from AxiomEmbedded 

AxiomEmbedded no longer vendors or preserves the AxiomEmbedded  starter inside this repository. The active repository contains the normalized AxiomEmbedded model; an external AxiomEmbedded  checkout can be supplied to the migration helper when needed.

The migration direction is:

```text
AxiomEmbedded  skill-centric
       ↓
AxiomEmbedded capability-centric
       ↓
Artifact graph + context engine
       ↓
Agent runtime + evidence ledger
```

Existing AxiomEmbedded  profiles, rules, skills and workflows can be treated as migration source material. New code should target the active AxiomEmbedded contracts rather than adding duplicated AxiomEmbedded -style packages.

## Compatibility mapping

| AxiomEmbedded  | AxiomEmbedded |
|---|---|
| `framework/schemas` | `schemas/` |
| `framework/taxonomy` | `taxonomies/` |
| `domains/*` | `domains/*` + `profiles/*` |
| `skills/*` | `skills/*` |
| `rulesets/*` | `rules/` |
| `workflows/*` | `workflows/*` |
| `traceability/*` | `packages/core/graph.py` + `schemas/trace-link.schema.json` |
| `quality-gates/*` | `packages/workflow/gates.py` + `workflows/*` |
| `technology-packs/*` | `platforms/*` + `skills/platforms/*` |
| `tool-adapters/*` | `tools/*` + `integrations/*` |

## External migration

Use the migration helper with an external AxiomEmbedded  checkout or extracted archive directory:

```bash
python scripts/migrate_AxiomEmbedded .py --source /path/to/AxiomEmbedded 
```

The AxiomEmbedded repository itself must not depend on that source tree for build, tests, CI, packaging, or runtime behavior.
