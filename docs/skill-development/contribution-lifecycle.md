# AxiomEmbedded Skill Contribution Lifecycle

## Overview

Every skill contribution follows a controlled 9-stage lifecycle. This ensures
that skills are developed, reviewed and released consistently without damaging
the rest of the system.

## Stages

### 1. Intake

Contributor selects one change type:
- `NEW` - Create a new skill
- `UPDATE` - Update an existing skill
- `SUBSKILL` - Create a sub-skill under an existing parent
- `SPLIT` - Split mixed content into domain-specific skills
- `DEPRECATE` - Deprecate an obsolete skill with migration plan
- `STANDARD-UPDATE` - Update standard metadata and assess affected skills

### 2. Repository discovery

Search the catalogue, related skills, parent/child relationships, domain maps,
standards, rules, agents, workflows and evaluation cases before making changes.

### 3. Gap assessment

Determine whether to:
- Update an existing skill
- Create a child skill
- Create an independent skill
- Split mixed content
- Reject a duplicate proposal

### 4. Skill design review

Agree on domain, activity, ID, applicability, standards, inputs, outputs,
relationships, maturity and acceptance criteria before implementation.

### 5. Authoring

Create or update the skill, templates, references, checklists, deterministic
scripts and test fixtures.

### 6. Integration

Update the canonical catalogue, domain maps, skill groups, agent routing,
relevant workflow and standards links.

### 7. Automated validation

Validate metadata, references, schemas, group matching, traceability, duplicate
content, output contracts and evaluation cases.

### 8. Independent review

Obtain domain expert review. Require additional qualified independent review
for safety-critical and security-sensitive changes.

### 9. Pull request and release

Run all CI checks, document evidence, update changelog and maturity, then
merge through the approved repository process.

## Contribution decision matrix

| Situation | Correct action |
|-----------|---------------|
| Existing skill covers same domain/activity but is incomplete | Update existing skill |
| Existing parent has a narrower reusable activity | Create a subskill |
| New domain has genuinely different process or evidence requirement | Create new domain skill |
| One skill mixes automotive and aerospace controls | Split into domain-specific skills |
| A standard changes edition or status | Update standard metadata and assess affected skills |
| Existing skill is obsolete | Deprecate with migration plan, not delete |
| Content is only a small instruction, not independent workflow | Add to existing skill or references |

## Naming conventions

Branch: `skills/<domain>/<activity>`
Commit: `skills(<domain>): <description>`
Skill ID: `axiom-<domain>-<activity>[-<standard-or-subsystem>]`

## Pull request requirements

- Change type and reason
- Existing skills inspected
- Domain and standard applicability
- New or changed skill IDs
- Parent, child and related skill links
- Templates, checklists and validation changes
- Evaluation results and known limitations
- Reviewer and approval requirements
