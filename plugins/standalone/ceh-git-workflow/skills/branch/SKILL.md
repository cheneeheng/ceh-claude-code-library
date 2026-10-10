---
name: branch
description: >-
  Load this skill when creating or naming a git branch, or starting new work from main: the prefix
  (feat/, fix/, chore/, docs/, test/, refactor/) and the short description.
disable-model-invocation: false
user-invocable: false
compatibility: >-
  Requires the git CLI on PATH and a git working tree. No network access, GitHub CLI, or language
  runtime is needed.
license: Apache-2.0
---

# Branch

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

3. For a long run that edits many files (a multi-task plan, an autonomous workflow) while the user
   keeps working in the same checkout, offer an isolated worktree before starting. Prefer Claude
   Code's own worktree (the `EnterWorktree` tool, or `claude --worktree <name>`) over a raw
   `git worktree add`, because Claude Code tracks it and cleans it up on exit. The worktree still
   gets a `<type>/<short-description>` branch. A Claude Code worktree branches from the default
   branch, not from the current `HEAD`, unless `worktree.baseRef` is `"head"` in `settings.json`,
   so check its base before building on unmerged work.

### Naming

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
