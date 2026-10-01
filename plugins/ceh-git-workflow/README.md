# ceh-git-workflow

Claude Code plugin delivering git workflow standards as skills. Covers trunk-based branching,
Conventional Commits, pull requests from opening to merge, code review conventions, changelog
entries, and releases. Everything here is stack-agnostic: language toolchains, coverage targets,
and package management belong in stack plugins.

Tier: **cross-cutting**. No plugin dependencies.

## Prerequisites

Each skill declares what it needs in its `compatibility` frontmatter. In short: the `git` CLI for
every skill, the GitHub CLI (`gh`, authenticated via `gh auth login`) for `pull-request` and
`release`, and Python 3 for the `update-changelog` validator. The plugin reads no environment
variables.

## Skills

Auto-trigger on context; each loads only the relevant content.

| Skill              | Auto-loads when                                                                                                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `branch`           | Creating or naming a branch                                                                                                                                                        |
| `commit`           | Writing or reviewing a commit message                                                                                                                                              |
| `pull-request`     | A branch is heading into `main`: opening a PR, merging one (or a local branch), or landing the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup |
| `release`          | Shipping a version: bump → changelog → PR → merge → tag → GitHub release. Also covers tag-only and the hotfix variant                                                              |
| `code-review`      | Writing PR review comments                                                                                                                                                         |
| `update-changelog` | Writing a `CHANGELOG.md` entry — a versioned section, or bullets under `[Unreleased]`                                                                                              |

`pull-request` and `release` each carry their full sequence inline and call only
`update-changelog`, so a compound request ("commit, PR and merge", "ship a release") loads two
skills rather than fanning out into one per step.

> README maintenance lives in the `ceh-readme` plugin, which both sequences use only when the
> change is user-facing, so it is not a declared dependency. `update-changelog` lives here because
> every input it reads is git (`git describe --tags`, `git log`, `git tag`, `git remote`).

## Scripts

| Script                    | Purpose                                                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/check-semver.py` | Validate `CHANGELOG.md` — semver format, date order, no duplicates; accepts `-` or `—` date separators (used by `update-changelog`) |

```bash
python3 scripts/check-semver.py CHANGELOG.md
```
