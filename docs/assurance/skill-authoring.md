# Assurance skill authoring guide

Follow the repo `docs/skill-authoring-guide.md` plus these assurance rules.

1. Flat `skills/axiom-<topic>[-review]` directories; no domain nesting.
2. `SKILL.md` frontmatter: name, title, description, version, author, license,
   domains, platforms, plus the `axiom:` block with dotted_name, subdomain
   (`assurance`, `safety`, or `cybersecurity`), maturity, related_skills
   (symmetric builder↔reviewer link), standards with edition/year.
3. Body must contain Purpose, Workflow, and Acceptance sections.
4. Declare every checklist/template/script path in the `axiom:` block; all
   declared files must exist.
5. Ship one YAML template with the full envelope and one deterministic
   `scripts/check_*.py` built on `packages/skills/assurance.py`.
6. Record new skills in `skills/catalog.yaml` and `skills/registry.yaml`;
   the `assurance` group in `skills/groups.yaml` should match them.
7. Run `python scripts/validate_skills.py --skill <id>` and the skill checker
   before opening a PR.
