# Assurance platform architecture

The assurance slice reuses AxiomEmbedded native layers; it adds no parallel
platform tree.

- `schemas/assurance-*.schema.json` — canonical artifact contracts plus the
  shared `assurance-envelope.schema.json` core.
- `packages/skills/assurance.py` — deterministic engines: artifact validation,
  cross-artifact traceability check, review-report builder.
- `skills/axiom-*` — ten flat skills (five builder plus five reviewer) in the
  existing skill tree, registered in `skills/catalog.yaml`, `skills/registry.yaml`,
  and the `assurance` view in `skills/groups.yaml`.
- `axiom_cli` — `artifact validate`, `trace check`, `review check` commands.
- `examples/industrial-robot-cell/` — worked end-to-end evidence.

Flow: scope → hazard-risk → safety-requirements → vnv-plan, with threat-model
branching from scope. Every builder output is reviewed by its paired reviewer
skill, which emits a separate append-only report and never edits the source.
