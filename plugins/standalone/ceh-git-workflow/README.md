# ceh-git-workflow

Claude Code plugin delivering git workflow standards as skills. Covers trunk-based branching,
Conventional Commits, pull requests from opening to merge, code review conventions, changelog
entries, README upkeep, and releases. Everything here is stack-agnostic: language toolchains, coverage targets,
and package management belong in stack plugins.

Stage: **Core**. No plugin dependencies.

## Prerequisites

Each skill declares what it needs in its `compatibility` frontmatter. In short: the `git` CLI for
every skill, the GitHub CLI (`gh`, authenticated via `gh auth login`) for `pull-request`,
`release` and workspace PR checkpoints, and `python3` on PATH (stdlib only) for the `update-changelog` validator and the
branch guard, skill-started guard and workspace sync hooks. The workspace sync hook also needs git 2.27 or later.
`write-code-review` and `write-period-retro` save YAML and render its Markdown through
[uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on first use. Without uv the
YAML is saved unchecked and the agent says the Markdown was not rendered.

## Skills

Auto-trigger on context; each loads only the relevant content.

| Skill                     | Auto-loads when                                                                                                                                                                                                                                                                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit`                  | Writing or reviewing a commit message                                                                                                                                                                                                                                                                                                   |
| `pull-request`            | A branch is heading into `main`: opening a PR, merging one (or a local branch), or landing the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup                                                                                                                                                      |
| `release`                 | Shipping a version: bump → changelog → PR → merge → tag → GitHub release. Also covers tag-only and the hotfix variant                                                                                                                                                                                                                   |
| `write-code-review`       | Writing PR review comments. A linked spec is checked on its own axis and reported in an Against the spec list. Say "panel review" for the same brief on two or three models, ranked by agreement (opt-in, several times the cost). Say "gate this PR" for two fresh reviewers who must both approve, up to three rounds                 |
| `address-review-comments` | Acting on review feedback on your own change, from a PR or the branch's saved review file. It's working if every comment gets a fixed, pushed-back, or answered line, a saved finding is ticked off with its resolution, and no reply agrees before quoting code or output                                                              |
| `update-changelog`        | Writing a `CHANGELOG.md` entry — a versioned section, or bullets under `[Unreleased]`                                                                                                                                                                                                                                                   |
| `update-readme`           | Keeping `README.md` accurate after a significant change: surgical edits behind a gate that does nothing when nothing material changed                                                                                                                                                                                                   |
| `write-period-retro`      | Looking back over a period: what shipped, how work flowed, and at most three issues from git history, each routed to the skill that fixes it. Saved to `.agents_workspace/product/retro/`, one file for every issue. It's working if every number names the command it came from, every issue names a route, and no line ranks a person |

`pull-request` and `release` each carry their full sequence inline and call only
`update-changelog` on every run, plus `update-readme` when the change is user-facing, so a compound
request ("commit, PR and merge", "ship a release") loads two or three skills rather than fanning
out into one per step.

> `update-changelog` and `update-readme` live here because both fire at the same git moment, a
> change about to land, and read git to do it (`git describe --tags`, `git log`, `git diff`).
> `update-readme` was the standalone `ceh-readme` plugin in agent-skills.

## Hooks

The plugin ships hooks (`hooks/hooks.json`) that activate automatically when the plugin is enabled.

| Hook                                        | Event                                                                                                                         | Script                                             | Default |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------- |
| [Branch guard](#branch-guard)               | `PreToolUse` (`Edit`, `Write`, `MultiEdit`, `NotebookEdit`)                                                                   | `branch-guard.py`                                  | on      |
| [Workspace sync](#workspace-sync)           | `SessionStart`, `PreToolUse` (`Bash`), `PostToolUse` (`EnterWorktree`), `Stop`, `SessionEnd`, `SubagentStart`, `SubagentStop` | `sync-agents-workspace.py`                         | on      |
| [Skill-started guard](#skill-started-guard) | `PreToolUse` (`Bash`, `Edit`, `Write`, `MultiEdit`)                                                                           | `skill-started-guard.py`                           | on      |
| [Artifact hooks](#artifact-hooks)           | `PostToolUse` and `PreToolUse` (`Edit`, `Write`, `MultiEdit`)                                                                 | `artifact-render-hook.py`, `generated-md-guard.py` | on      |

### Branch guard

Denies a file edit when the file sits in a git work tree whose checked-out branch is the default
branch (`origin/HEAD`, or `main` / `master`), and tells the agent to create a feature branch first, naming the
prefixes (`feat/`, `fix/`, `chore/`, `docs/`, `test/`, `refactor/`). Uncommitted work carries over with `git checkout -b`. This turns "branch before
implementing" from an instruction the model can forget into one it cannot skip.

A git-ignored file is allowed, because it is never committed. Only the session's own repository is guarded, its worktrees included: files outside a git work
tree pass, as do files in any other repository, whatever branch it is on, and detached and unborn
`HEAD`s. The guard covers the file
tools only: a `Bash` write (`sed -i`, `>`) on the default branch still goes through, so it is a
nudge with teeth rather than a sandbox. It fails open: unparseable input, a missing `git`, or a
crashed interpreter allows the edit. After three full denials in a session it sends one line with
the denial's number, because repeating an identical block pushes the model into loops.

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to undo it.

| Variable             | Default              | Effect                                                                                |
| -------------------- | -------------------- | ------------------------------------------------------------------------------------- |
| `CEH_BRANCH_GUARD`   | unset (guard on)     | `off` allows edits on the default branch, for when the user asked to edit it in place |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook script names to skip; `branch-guard` switches this guard off     |

### Workspace sync

Brings a project's nested `.agents_workspace` git repo (decision log, handoffs, notes) into a git
worktree. A worktree is a fresh checkout of tracked files, so without it a worktree session sees no
workspace. A link would not do: Claude Code's worktree isolation refuses Edit and Write through a
link to a folder outside the worktree.

- **Session start in a worktree, or `EnterWorktree`:** adds `<worktree>/.agents_workspace` as a git worktree of the main
  checkout's workspace repo, on the branch `ceh-ws/<X>/<worktree folder>`, where `<X>` is the branch
  the main workspace has checked out. A branch left by an earlier worktree of the same name is
  reused.
- **After every turn:** commits the worktree's workspace changes to that branch, so removing the
  worktree loses only what changed since the last turn. The commit's subject is
  `chore(workspace): sync worktree <worktree folder>`.
- **After every turn in a main checkout:** commits the main workspace's pending changes, after any
  PR checkpoint below, with the subject `chore(workspace): sync session <first 8 characters of
the session id>` and the changed paths in the body. It skips while a merge, an autostash or an
  index lock is in progress, and warns once per session when the commit fails. Each turn's files
  are committed at its end, so an agent that wants a subject naming what it wrote commits the
  workspace itself before the turn ends. At `SessionStart` the hook tells the agent to do so, and
  the `commit` skill's Workspace section says how.
- **Attribution:** every workspace commit the hook makes ends with your `attribution.commit` line,
  read from `.claude/settings.local.json` in the main checkout, then the project's
  `.claude/settings.json`, then `settings.json` in `$CLAUDE_CONFIG_DIR` or `~/.claude`. The first
  file that sets the key decides, and `false` or `""` leaves the line out. Managed settings and
  `--settings` are not read.
- **Session end:** starts a background process and returns at once, because `SessionEnd` hooks get
  1.5 s that a plugin cannot raise. In a worktree, the process commits once more and merges the
  branch into `<X>`, autostashing uncommitted changes in the main workspace. When Claude Code
  reports the main checkout at exit, it catches up as below. `DECISION_LOG.md` merges with git's
  `union` driver, so two sessions appending both keep their lines. Other files merge normally.
- **Session start in a main checkout:** merges every `ceh-ws/<X>/` branch left over, for example
  when a session crashed or its background merge was killed, deletes merged branches no worktree
  holds, and tells the agent which branch failed to merge and how to merge it by hand.

Before a `gh pr merge` command, the hook records its PR number, URL or branch as pending,
without calling GitHub. At Stop it checks pending entries for that checkout. Once GitHub confirms
a recent merge, it makes an empty commit with a subject such as
`chore(workspace): checkpoint source pr #123` and a body containing the PR URL and merge commit.
The checkpoint holds no files, staged or not, so it never files unrelated work under a PR's name.
Uncommitted workspace changes go into the same Stop's `chore(workspace): sync ...` commit. Several confirmed PRs share one checkpoint commit. Repeated merge events are cleared when
Git history already holds that PR and merge commit. The commit stays local.

Pending entries live in the main workspace's `.git/ceh-checkpoint-pending/`. An open PR stays
pending even if its merge command was denied or failed. A queued auto-merge is checked at a later
Stop in the same checkout, so its checkpoint commit is made at that later time. Closed
PRs, older merges and entries older than 14 days are cleared without a checkpoint. Merges made
only in a browser are not recorded. Commands targeting another repo with `-R` or `--repo` are
ignored. Lookup or commit failures keep the entry and show a message once per session and reason,
naming the pending folder. Ordinary sync failures remain silent.

It never pushes or aborts a merge it did not start, and a sync hook must never stop a session.
It does nothing without a `.agents_workspace` git repo in the main
checkout, when that repo is on a detached `HEAD`, or in a bare repo. A subagent with
`isolation: "worktree"` gets the same workspace on `SubagentStart`, and on `SubagentStop` its
workspace is committed, its PR checkpoints made, and its branch merged into the main workspace
before the hook returns, retried while parallel subagents hold the index. The subagent's report
can reach the caller before that merge, so read its records once its completion notice arrives.
The merge stashes the main workspace's uncommitted changes and reapplies them, so an edit landing
in between can stay in the stash: `git -C .agents_workspace stash list` shows it. A subagent
without isolation shares the caller's checkout and changes nothing here. On Windows, a job object that
kills its children and forbids breakaway would kill the background merge; the next session start
then merges. `CEH_DISABLED_HOOKS` with `sync-agents-workspace` switches it off.

### Skill-started guard

Denies a call until a skill that owns its moment has been started in the session, by a `Skill`
tool call or a slash command, and names the skill to invoke:

| Call                                 | Owning skills                   |
| ------------------------------------ | ------------------------------- |
| `git commit` in a `Bash` command     | `commit`                        |
| An edit or write of a `CHANGELOG.md` | `update-changelog` or `release` |
| An edit or write of a `README.md`    | `update-readme`                 |

A skill another skill's steps only name ("following `commit`") still has to be started: that
wording is how all three were skipped in one session. Files outside the session's project pass,
and so does `git commit` quoted inside another command, such as a `grep`. A subagent reads its own
transcript, so it starts the skill itself. It fails open. `CEH_SKILL_STARTED_GUARD=off`, or
`CEH_DISABLED_HOOKS` with `skill-started-guard`, switches it off.

### Artifact hooks

`artifact-render-hook.py` (PostToolUse) checks a written code review (`code-review/v3`) or period
retro (`period-retro/v3`) YAML against its model and renders its Markdown. The check needs `uv`;
without it the agent is told once per session that the file went unchecked.
`generated-md-guard.py` (PreToolUse) denies a hand edit to the generated Markdown, which the next
render would overwrite. `CEH_ARTIFACT_CHECK=off` turns both off, and `CEH_DISABLED_HOOKS` turns
off either by name.

## Scripts

| Script                                                             | Purpose                                                                                                                                                                                                           |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/branch-guard.py`                                          | `PreToolUse` hook: deny file edits on the default branch (see [Branch guard](#branch-guard))                                                                                                                      |
| `scripts/sync-agents-workspace.py`                                 | Workspace sync and PR checkpoint hook on `SessionStart`, `PreToolUse` (`Bash`), `PostToolUse` (`EnterWorktree`), `Stop`, `SessionEnd`, `SubagentStart` and `SubagentStop` (see [Workspace sync](#workspace-sync)) |
| `scripts/skill-started-guard.py`                                   | `PreToolUse` hook: deny a commit, changelog or README edit until its skill was started (see [Skill-started guard](#skill-started-guard))                                                                          |
| `scripts/artifact-render-hook.py`, `scripts/generated-md-guard.py` | The artifact hooks (see [Artifact hooks](#artifact-hooks))                                                                                                                                                        |
| `scripts/artifact.py`, `skills/<skill>/scripts/artifact.py`        | Check a code review or period retro YAML against its model, or render its Markdown, through uv                                                                                                                    |
| `skills/update-changelog/scripts/check-semver.py`                  | Validate `CHANGELOG.md` — semver format, date order, no duplicates; accepts `-` or `—` date separators (used by `update-changelog`)                                                                               |

```bash
python3 skills/update-changelog/scripts/check-semver.py CHANGELOG.md
```

## Where its files live

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`. A project with a root `product/` moves each file to the same sub-path there, or names its location in `CLAUDE.md`.
