---
name: hotfix
description: >-
  Load this skill when executing a critical production fix: branching from main with the
  fix/critical- prefix, keeping the fix minimal in scope, opening a PR with the required approval,
  and tagging a PATCH release after merge. Auto-load whenever a critical bug is being fixed
  directly, a hotfix branch is being created, or a PATCH release is being cut after an urgent fix.
compatibility: >-
  Requires the git CLI on PATH, the GitHub CLI (`gh`) installed and authenticated via `gh auth
  login`, a git repository with a GitHub remote, push permission, and network access. Verifying
  the fix additionally requires the target repo's own test toolchain, which this skill does not
  assume is installed.
---

# Hotfix Workflow

For P1/P2 production issues that cannot wait for the next normal release.

## Procedure

1. **Branch:** `fix/critical-<description>` from `main`
2. **Scope:** Minimal fix only — no unrelated changes
3. **Review:** 1 approval minimum, fast-tracked
4. **CI:** All checks must pass — do **not** skip CI under pressure. A broken hotfix is worse than
   a delayed one.
5. **Merge:** Merge commit to `main` (never squash — preserve the commits)
6. **Tag:** Bump PATCH version, apply tag
7. **Deploy:** Staging → production (abbreviated but both still required)

## Commands

```bash
git checkout main && git pull origin main
git checkout -b fix/critical-<description>

# Fix and commit (minimal scope only)
git add <files>
git commit -m "fix(<scope>): <description>"

# Push and open PR (1 approval minimum, all CI must pass)
git push -u origin fix/critical-<description>
gh pr create --title "fix(<scope>): <description>"

# After merge — bump PATCH version, tag, clean up
git checkout main && git pull origin main
# Bump the PATCH version in the project manifest(s), then:
git add <manifest files>
git commit -m "chore: bump version to v<X.Y.Z>"
git push origin main
git tag -a v<X.Y.Z> -m "v<X.Y.Z> — <symptom fixed>"   # annotated: some repos enforce it
git push origin v<X.Y.Z>
git branch -d fix/critical-<description>
git push origin --delete fix/critical-<description>
```

## Rules

- The PR body links the incident and names the symptom, so the merge commit explains itself in
  `git log`.
- **Verify in production** — confirm the original symptom is gone and error rates/latency are back
  to baseline before declaring the incident resolved. Be ready to roll back if not.
- **Post-mortem** — for P1/P2, write one within 48 hours; saying "write a post-mortem" loads the
  format. The hotfix closes the bleeding; the post-mortem prevents the recurrence.
