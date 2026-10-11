# MCP Tool Backlog (spec pkg; implementation phased)

Existing: version/doctor/analyze/graph_build/context_select/impact/profile_validate/workflow_plan/route/engage/packs/compose/run_plan/read_skill/list_skills/list_profiles/status/fix/feature/research/install.

New (this framework):
- get_skill {skill_id} -> {manifest, body}: read path-sanitized SKILL.md. Priority P0. Implemented via axiom_sdk.read_skill.
- search_skills {query, domain, lifecycle, standard, artifact, mcp_tool} -> ranked list. P0. Pure index search, deterministic.
- validate_skill {skill_id} -> {valid, errors[], warnings[]}. P0. No writes.
- create_skill {skill_id, domain, title, --dry-run} -> scaffold paths. P1. Path-restricted writes under skills/.
- run_skill {skill_id, repo_path, target_files[], objective, constraints, output_dir, dry_run} -> run manifest + files. P1. Dry-run default; writes only under output_dir/.axiom/runs.
- analyze_repository, generate_report, generate_checklist, generate_test_plan, review_configuration, analyze_trace, generate_traceability_matrix: thin wrappers that load the matching axiom-* skill context and emit templated artifacts. P1. IMPLEMENTED 2026-10-11 in packages/skill_tools.py (SDK + 7 MCP tools, 26 -> 33 tools total; tests/test_skill_tools.py).

Security: input sanitization (skill_id allowlist ^[a-z0-9-]+$), path restriction (repo-relative, no ..), no secrets in logs, no network, no shell. Determinism: sorted output, no timestamps in bodies (manifest carries timestamp). Tests: schema + negative (bad id, traversal, missing skill) + golden-file.
