# AxiomEmbedded for GitHub Copilot

## MCP (coding agent / chat with MCP support)

Add `clients/mcp.json` to your MCP configuration. Tools available:

- `engage(domain, platform)` — skill slice for the project
- `run_plan(request, domain, platform)` — plan-then-execute plan
- `read_skill(skill_id)` — full SKILL.md + manifest
- `list_skills` / `list_profiles` — discovery

## CLI (terminal / custom agent)

```bash
python -m axiom_cli engage --domain automotive --platform mcu
python -m axiom_cli run "add watchdog supervision" --domain automotive --platform mcu
```

## REST (web app / service integration)

```bash
python -m axiom_cli serve --port 8931
curl -X POST localhost:8931/v1/engage -d '{"domain":"automotive","platform":"mcu"}'
```

Approval gate: execution beyond planning (push, release, destructive,
safety/security-critical changes) requires human approval per
`configs/project.yaml` — the agent must surface the plan first.
