# Integration Plan (minimal risk)

1. Additive only: new dirs `skills/axiom-*/`, `skills/_templates/`, `packages/skills/{registry,loader,validator,runner}.py`, `scripts/{validate_skills,create_skill}.py`; no moves/deletes.
2. Dual-catalog: add `skills/catalog.yaml` (rich) + `skills/registry.yaml` (prompt2 shape); extend `registries/skill-index.json` + `registries/skills.json` entries for new skills via script (keeps test_index_linkage green).
3. New skills carry BOTH contracts: legacy frontmatter {name,description,version,domains,platforms} + `axiom:` block; plus `manifest.yaml` with facets (keeps test_manifests green).
4. CLI/MCP additions only (no signature changes): `axiom skills list|validate|run|create|report`; MCP tools `get_skill`, `search_skills`, `validate_skill`, `create_skill`, `run_skill` (+ generators as skill-context wrappers).
5. Backups: work happens on branch `feature/automotive-skill-framework`; migration report lists every touched file; `sync_clients.py --check` unaffected (new skills opt-in to index only).
6. Verification after each phase: compileall, pytest -q, doctor --skip-tests, repo validate, validate_skills.
