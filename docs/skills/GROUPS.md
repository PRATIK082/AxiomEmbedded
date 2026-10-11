# Skill groups (smart views for 1000+ skills)

Groups are **named rules evaluated against `skills/catalog.yaml`**, not
folders. Nothing moves on disk when the library grows past 1000 skills:
a new skill joins its groups automatically when its `id`, `subdomain`,
`domain`, `tags`, or `maturity` matches a rule.

## Rules (`skills/groups.yaml`)

```yaml
groups:
  diagnostics:
    title: Vehicle diagnostics
    match_any:                       # OR across clauses ...
      - {subdomain: [diagnostics]}   # ... AND across keys, OR within a list
      - {id: [automotive-diagnostics]}
```

Match keys: `id`, `id_prefix`, `domain`, `subdomain`, `tags`, `maturity`.
Unknown keys are a hard error (`ValueError`), so typos fail fast.

**Invariant (CI-enforced): every enabled catalog skill matches >= 1 group.**
`validate_groups()` returns violations; `sync_skill_index` hard-errors on
them; `.pre-commit` + nightly drift keep it green. If you add a skill that
matches nothing, either widen a rule or add a group — never leave it
orphaned.

## Using groups

| Surface | Usage |
|---|---|
| Engage (scoped discovery) | `axiom engage --group diagnostics [--domain automotive] [--limit 20]` |
| MCP | `engage` tool with `group` / `limit` (`total`, `truncated` in reply) |
| Install (copy subset) | `axiom install --client opencode --groups diagnostics,safety-security` |
| Index | `registries/skill-index.json → by_group` (matcher == index, tested) |

`--groups` ANDs with `--domains`: a skill copies only if it passes both
filters (`domains=[all]` shared skills always pass the domain side).
`--limit 0` (default) means all; any positive cap sets `truncated: true`
and reports `total` so agents can page.

## Adding a group (no code change)

1. Append to `skills/groups.yaml` under `groups:`.
2. Run `axiom skills apply` — index, `by_group`, and mirrors regenerate.
3. CI (`pipeline --check` + `test_by_group_index_matches_matcher`) proves
   the index equals the matcher and coverage is still 100%.
