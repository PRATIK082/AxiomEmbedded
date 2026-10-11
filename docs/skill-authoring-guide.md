# Skill Authoring Guide (canonical)

See `docs/skills/AUTHORING_GUIDE.md` for the full guide.

Walkthrough (create + run one skill):

```bash
python scripts/create_skill.py --id axiom-automotive-can-review \
  --title "CAN Design Review" --domain automotive --apply
# fill SKILL.md, checklist, template, script, tests
python scripts/validate_skills.py --skill axiom-automotive-can-review
python -m axiom_cli skills run axiom-automotive-can-review \
  --objective "Review DBC change" --target net/body.dbc
python -m axiom_cli skills run axiom-automotive-can-review \
  --objective "Review DBC change" --target net/body.dbc --apply
```
