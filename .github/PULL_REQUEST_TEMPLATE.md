## Skill Change Pull Request

### Change type
- [ ] NEW
- [ ] UPDATE
- [ ] SUBSKILL
- [ ] SPLIT
- [ ] DEPRECATE
- [ ] STANDARD-UPDATE

### Reason
<!-- Why is this change needed? -->

### Existing skills inspected
<!-- List the skills, catalogue entries, domain maps and standards reviewed. -->

### Domain and standard applicability
<!-- Primary domain, supported domains, applicable standards and editions. -->

### New or changed skill IDs
<!-- List the skill IDs being added, modified or deprecated. -->

### Parent, child and related skill links
<!-- Describe the skill graph relationships. -->

### Templates, checklists and validation changes
<!-- What deliverables, templates, scripts and tests are included? -->

### Evaluation results and known limitations
<!-- Test results, eval coverage and known gaps. -->

### Reviewer and approval requirements
<!-- Who must review this? Safety/security critical? -->

### Checklist
- [ ] `python scripts/skill_pipeline.py --check` passes
- [ ] `python -m pytest -q` passes
- [ ] `python -m axiom_cli doctor` passes
- [ ] Skill counts updated in README/docs if changed
- [ ] Standards registry updated if standard changed
- [ ] Domain profile updated if new domain
- [ ] Changelog updated
