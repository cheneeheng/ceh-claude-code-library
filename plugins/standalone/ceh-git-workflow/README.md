# ceh-git-workflow

Claude Code plugin delivering git workflow standards as skills. Covers trunk-based branching,
Conventional Commits, pull requests from opening to merge, code review conventions, changelog
entries, README upkeep, and releases. Everything here is stack-agnostic: language toolchains, coverage targets,
and package management belong in stack plugins.

Tier: **cross-cutting**. No plugin dependencies.

## Prerequisites

Each skill declares what it needs in its `compatibility` frontmatter. In short: the `git` CLI for
every skill, the GitHub CLI (`gh`, authenticated via `gh auth login`) for `pull-request` and
`release`, and `python3` on PATH (stdlib only) for the `update-changelog` validator and the
branch guard hook.

## Skills

Auto-trigger on context; each loads only the relevant content.

| Skill                     | Auto-loads when                                                                                                                                                                                                                                                                                                         |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `branch`                  | Creating or naming a branch                                                                                                                                                                                                                                                                                             |
| `commit`                  | Writing or reviewing a commit message                                                                                                                                                                                                                                                                                   |
| `pull-request`            | A branch is heading into `main`: opening a PR, merging one (or a local branch), or landing the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup                                                                                                                                      |
| `release`                 | Shipping a version: bump → changelog → PR → merge → tag → GitHub release. Also covers tag-only and the hotfix variant                                                                                                                                                                                                   |
| `code-review`             | Writing PR review comments. A linked spec is checked on its own axis and reported in an Against the spec list. Say "panel review" for the same brief on two or three models, ranked by agreement (opt-in, several times the cost). Say "gate this PR" for two fresh reviewers who must both approve, up to three rounds |
| `address-review-comments` | Acting on review feedback on your own change. It's working if every comment gets a fixed, pushed-back, or answered line, and no reply agrees before quoting code or output                                                                                                                                              |
| `update-changelog`        | Writing a `CHANGELOG.md` entry — a versioned section, or bullets under `[Unreleased]`                                                                                                                                                                                                                                   |
| `update-readme`           | Keeping `README.md` accurate after a significant change: surgical edits behind a gate that does nothing when nothing material changed                                                                                                                                                                                   |
| `write-engineering-retro` | Looking back over a period: what shipped, how work flowed, at most three changes, all from git history into `.agents_workspace/retros/`. It's working if every number names the command it came from and no line ranks a person                                                                                         |

`pull-request` and `release` each carry their full sequence inline and call only
`update-changelog` on every run, plus `update-readme` when the change is user-facing, so a compound
request ("commit, PR and merge", "ship a release") loads two or three skills rather than fanning
out into one per step.

> `update-changelog` and `update-readme` live here because both fire at the same git moment, a
> change about to land, and read git to do it (`git describe --tags`, `git log`, `git diff`).
> `update-readme` was the standalone `ceh-readme` plugin in agent-skills.

## Hooks

The plugin ships hooks (`hooks/hooks.json`) that activate automatically when the plugin is enabled.

| Guard                         | Event                                                       | Script            | Default |
| ----------------------------- | ----------------------------------------------------------- | ----------------- | ------- |
| [Branch guard](#branch-guard) | `PreToolUse` (`Edit`, `Write`, `MultiEdit`, `NotebookEdit`) | `branch-guard.py` | on      |

### Branch guard

Denies a file edit when the file sits in a git work tree whose checked-out branch is the default
branch (`origin/HEAD`, or `main` / `master`), and tells the agent to create a feature branch per
`branch` first. Uncommitted work carries over with `git checkout -b`. This turns "branch before
implementing" from an instruction the model can forget into one it cannot skip.

Files outside a git work tree pass, as do detached and unborn `HEAD`s. The guard covers the file
tools only: a `Bash` write (`sed -i`, `>`) on the default branch still goes through, so it is a
nudge with teeth rather than a sandbox. It fails open: unparseable input, a missing `git`, or a
crashed interpreter allows the edit. After three full denials in a session it sends one line with
the denial's number, because repeating an identical block pushes the model into loops.

| Variable             | Default              | Effect                                                                                |
| -------------------- | -------------------- | ------------------------------------------------------------------------------------- |
| `CEH_BRANCH_GUARD`   | unset (guard on)     | `off` allows edits on the default branch, for when the user asked to edit it in place |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook script names to skip; `branch-guard` switches this guard off     |

## Scripts

| Script                    | Purpose                                                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/branch-guard.py` | `PreToolUse` hook: deny file edits on the default branch (see [Branch guard](#branch-guard))                                        |
| `scripts/check-semver.py` | Validate `CHANGELOG.md` — semver format, date order, no duplicates; accepts `-` or `—` date separators (used by `update-changelog`) |

```bash
python3 scripts/check-semver.py CHANGELOG.md
```
