# Using AxiomEmbedded skills (v1.2.0 packaging)

Every skill is now a self-describing **agent skill**: `skills/<id>/SKILL.md`
carries YAML frontmatter (`name`, `description`, `version`, `domains`,
`platforms`) that Claude Code, OpenCode, Codex, and Antigravity all use for
auto-discovery. Facets are declared once in `registries/skill-facets.yaml`;
`registries/skill-index.json` holds the generated forward + reverse linkage.

## Are domains and platforms interlinked?

Yes — three ways, all generated from the same source:

1. **Skill facets.** Each skill lists its `domains` and `platforms`
   (`all` = matches any filter). See `registries/skill-facets.yaml`.
2. **Reverse index.** `registries/skill-index.json` maps `by_domain` and
   `by_platform` back to skill lists, so UIs can browse domain-first.
3. **Profiles.** `profiles/<domain>-<platform>.yaml` (e.g. `automotive-mcu`,
   `robotics-ai`) bundle a domain + platform + capability set; `axiom engage`
   suggests matching profiles for your selection.

## Engage only what your project needs

```bash
# Which skills apply to an automotive MCU project?
python -m axiom_cli engage --domain automotive --platform mcu

# Robotics on an MPU running Linux?
python -m axiom_cli engage --domain robotics --platform mpu

# Everything (no filters)
python -m axiom_cli engage
```

Output lists the engaged `skills`, matching `profiles`, and the exact
`context_files` (`skills/<id>/SKILL.md`) to load — load only those into the
model context, nothing else.

## Standalone agent run (opencode-like)

```bash
python -m axiom_cli run "add watchdog supervision to the motor driver" --domain automotive --platform mcu
```

`axiom run` engages skills, routes intent, and emits a plan-then-execute plan
(phases, context files, approval gates). The host harness provides the model;
axiom decides **what to load and in what order**. Pushing, releasing, or
safety/security-critical changes still require human approval
(`configs/project.yaml`).

## Install into your harness

```bash
# Full pack
python scripts/install_skills.py --harness claude --dest .claude/skills

# Domain/platform slice only
python scripts/install_skills.py --harness opencode --dest .opencode/skills --domain automotive --platform mcu
```

| Harness | Skills directory | Notes |
|---------|-----------------|-------|
| Claude Code | `.claude/skills/` (project) or `~/.claude/skills/` (personal) | Frontmatter `name` + `description` enable auto-discovery |
| OpenCode | `.opencode/skills/` | Same layout; repo `opencode.json` already configures the project |
| Codex | `.codex/skills/` | Same `SKILL.md` + frontmatter format |
| Antigravity | `.antigravity/skills/` | Same `SKILL.md` + frontmatter format |

After install, invoke by name ("use the `mcu` skill") or let the harness
auto-discover from the `description` triggers.
