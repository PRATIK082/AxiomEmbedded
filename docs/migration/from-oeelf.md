# Migrating from the current AxiomEmbedded  starter

The original AxiomEmbedded  starter is treated as external migration input. Its skills carry repeated metadata/schema/workflow/checklist bundles; the AxiomEmbedded migration target is compositional.

| Current AxiomEmbedded  | AxiomEmbedded | Action |
|---|---|---|
| `skills/**/SKILL.md` | `skills/<capability>/` | retain capability semantics, remove duplicated boilerplate |
| `domains/**` | `domains/**` | keep as overlays; add manifests and applicability metadata |
| `technology-packs/**` | `platforms/**` | normalize platform/OS/technology hierarchy |
| `framework/schemas/**` | `schemas/**` | expand into artifact/agent/evidence/change contracts |
| `workflows/**` | `workflows/**` | make workflows data-driven and reusable |
| `profiles/**` | `profiles/**` | compose domain + platform + standards + lifecycle |
| `quality-gates/**` | `policies/gates/**` | drive gates from profile and evidence state |
| `traceability/**` | `packages/core/graph.py` + `schemas/trace-link.schema.json` | make traceability part of the artifact graph |
| `scripts/compose_profile.py` | `packages/workflow` + CLI | implement actual composition/conflict detection |
| `scripts/assess_middle_entry.py` | brownfield + entry assessment | connect gaps to artifacts, risks and evidence |
| `tool-adapters/` | `integrations/` | provider/client/protocol adapters stay outside core |

Do not add the AxiomEmbedded  repository as a vendored subtree. Validate mappings against an external AxiomEmbedded  source before migrating selected content.
