---
name: git
description: Git workflow discipline for clean history, safe branching, review-ready commits, controlled merges/rebases, tags, and recovery. Use when creating branches, committing, merging, rebasing, tagging, syncing remotes, or recovering repository state.
version: 1.2.0
domains: [all]
platforms: [all]
axiom:
  dotted_name: axiom.legacy.git
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  - git
  - version-control
  related_skills:
  - configuration-management
  - change-impact
  - release
  - code-review
  - debugging
  - documentation
  checklists:
  - checklists/git-checklist.md
---

# Git skill

Git hygiene and workflow for embedded and cross-domain engineering: every change
is traceable, reviewable, and reproducible, with history that supports bisect,
audit, and release.

## 1. Purpose and scope

**Purpose.** Keep repository history accurate, minimal, and reversible so any
shipped artifact maps to an exact source revision and any defect can be traced
and bisected.

**In scope.** Branching strategy, commit granularity and messages, staging
discipline, merge vs. rebase decisions, conflict resolution, tagging and
release points, remote synchronization, hooks, submodules/worktrees, and
recovery (reflog, reset, revert, cherry-pick).

**Non-goals.** Hosting-provider specifics (GitHub/GitLab UI), CI pipeline
definition (see `axiom-embedded-cicd`), and release ceremonies (see `release`).
Ends at an auditable, recoverable repository state.

## 2. Normative sources (high confidence)

| # | Source | Version / status | Clause / scope | URL |
|---|--------|------------------|----------------|-----|
| 1 | Git | 2.x | Reference manual: branching, merging, rebasing, tagging, recovery | `https://git-scm.com/docs` |
| 2 | Conventional Commits | 1.0.0 | Commit message structure and semantic hints | `https://www.conventionalcommits.org/en/v1.0.0/` |
| 3 | Pro Git | 2nd ed. | Distributed workflows and recovery patterns | `https://git-scm.com/book/en/v2` |

## 3. Rules

1. **Branch from a known-good base.** Create feature/fix branches from the latest
   reviewed base (`main` or release branch), never from an unreviewed WIP tip.
2. **One logical change per commit.** Each commit builds, passes its targeted
   tests, and is independently reviewable; do not mix refactor, feature, and
   formatting in one commit.
3. **Meaningful commit messages.** Use a conventional type (`feat`, `fix`,
   `docs`, `refactor`, `test`, `chore`, `ci`) plus scope and imperative
   subject; body explains why and references issue/requirement IDs.
4. **Stage intentionally.** Review `git diff --cached` before committing; never
   commit secrets, generated artifacts, or unrelated files. Prefer `git add -p`.
5. **Keep history linear where practical.** Rebase feature branches onto the
   base before merge; use merge commits only for integration points or release
   baselines that must remain visible.
6. **No history rewrite on shared branches.** Never force-push `main`, release,
   or any branch others depend on; use `git revert` for published corrections.
7. **Tag immutably.** Release tags are annotated, signed when policy requires,
   and never moved or deleted after publication; tags reference exact commits.
8. **Recover, don't panic.** Prefer `git reflog`, `git revert`, and
   `git cherry-pick` over destructive resets; `git reset --hard` requires an
   explicit, recorded justification.
9. **Sync safely.** Pull with `--ff-only` or rebase; resolve conflicts
   deliberately and re-run tests before pushing.
10. **Submodules/worktrees pinned.** Record submodule commits and worktree
    paths; never leave a repository in a detached or half-merged state without
    a documented reason.
11. **No generated build outputs or local index artifacts.** Never commit
    client mirrors (`.opencode/`, `.claude/`, `.claude-plugin/`) or generated
    index output (`.axiom/`). Keep them ignored/untracked and remove them from
    the index if they were accidentally committed.

## 4. Decision rules

- **Merge vs. rebase:** rebase for private feature branches to keep linear
  history; merge for shared/release branches to preserve integration evidence.
- **Reset vs. revert:** reset only for local, unpublished mistakes; revert for
  anything pushed or released.
- **Squash vs. preserve:** squash noisy WIP commits before review; preserve
  commits that each carry independent review or bisect value.
- **Conflict resolution:** prefer minimal edits that keep both intents; rerun
  affected tests and static analysis before continuing.

## 5. Agent mode (headless) operating notes

- Read-only commands (`status`, `diff`, `log`, `show`, `branch`) may run without
  prompts.
- Mutating commands (`add`, `commit`, `merge`, `rebase`, `tag`, `push`) require
  the declared approval gate; `git push` always requires human approval per
  `configs/project.yaml`.
- Never run destructive commands (`reset --hard`, `clean -fdx`, `push --force`)
  without an explicit, recorded instruction and impact assessment.
- Always report the resulting commit hash, branch, and status after mutating
  operations.

## 6. Release gates (blocking)

1. Working tree clean or all changes explicitly accounted for.
2. Branch is up to date with its base or divergence is explained.
3. Commit messages follow the agreed convention and reference tracked work.
4. Required tests pass on the tip commit.
5. Release tags are annotated and point to the released commit.
6. No secrets or generated artifacts are committed.
7. No generated client mirrors (`.opencode/`, `.claude/`, `.claude-plugin/`) or
   generated index output (`.axiom/`) is committed.

## 7. Verification of this skill (Phase 4 gate)

- Sources cited with version and URL (S2).
- Branching/commit/tag rules are testable by repository policy checks.
- Recovery procedures are documented and exercised in at least one drill.
- No normative text copied; citations are identifiers/URLs only.

## 8. Common failure modes

- **Accidental secret commit:** stop pushing, rotate the secret, use history
  rewrite only on unpublished branches; record an incident note.
- **Diverged shared branch:** do not force-push; reconcile with merge and
  document the integration commit.
- **Lost work:** check `git reflog` and `git fsck` before declaring loss;
  recover via cherry-pick into a new branch.
- **Submodule drift:** pin the expected commit and verify with `git submodule
  status` in CI.

## 9. Guardrails

- Never bypass approval gates for push/release/destructive commands.
- Never claim compliance or certification from git hygiene checks.
- Do not rewrite published history without an approved change record.