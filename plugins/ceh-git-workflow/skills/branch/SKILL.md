---
name: branch
description: >-
  Load this skill when creating or naming a branch: choosing the correct prefix (feat/, fix/,
  chore/, docs/, test/, refactor/), formatting the short description, or starting new work from
  main. Auto-load whenever a new git branch is being created, a branch name is being chosen, or work
  is being started from the main branch.
compatibility: >-
  Requires the git CLI on PATH and a git working tree. No network access, GitHub CLI, or language
  runtime is needed.
---

# Branching

Trunk-based development. `main` is always deployable. Branch from `main` only — never from
another feature branch. Delete branches after merge.

## Procedure

1. Start new work from an up-to-date `main`:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b <type>/<short-description>
   ```

2. For anything long-lived, keep the branch current by rebasing on `main` rather than merging
   `main` in — it keeps history linear and the eventual PR diff clean:

   ```bash
   git fetch origin
   git rebase origin/main
   git push --force-with-lease     # your own branch only; --force-with-lease, never --force
   ```

   Do this before opening the PR and again if `main` moves ahead while the PR is in review.

## Branch naming

```
<type>/<short-description>
```

| Prefix      | When to use                                    | Example                            |
| ----------- | ---------------------------------------------- | ---------------------------------- |
| `feat/`     | New feature                                    | `feat/session-replay`              |
| `fix/`      | Bug fix                                        | `fix/token-expiry-edge-case`       |
| `chore/`    | Maintenance, tooling, dependency updates       | `chore/update-dependencies`        |
| `docs/`     | Documentation only                             | `docs/add-onboarding-guide`        |
| `test/`     | Test additions or fixes with no source changes | `test/reasoning-engine-invariants` |
| `refactor/` | Code changes without feature or bug changes    | `refactor/extract-auth-middleware` |

Short description: lowercase, hyphen-separated, 3–5 words.

## Rules

- Branch from `main` only, so every branch starts from a deployable state and its diff stays
  scoped to one concern — branching off another feature branch entangles unmerged work and bloats
  the eventual PR.
- Rebase is fine locally during development.
- Force-push is allowed only on your own feature branch (never on `main`).
