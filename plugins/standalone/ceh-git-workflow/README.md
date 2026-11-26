# ceh-git-workflow

Git habits the agent keeps in every repo: work on a branch, write Conventional Commits, take a pull
request from opening to merge, review code, keep the changelog and README current, and ship
releases. It works with any language. Toolchains, coverage targets and package management belong
in the stack plugins.

What it does for you:

- **Keeps `main` clean.** A guard stops file edits while the default branch is checked out.
- **Lands a branch in one pass.** Changelog, commit, PR, merge and cleanup, from one request.
- **Reviews and answers reviews.** Review someone else's PR, or work through the comments on yours.
- **Looks back.** A retro over a period of git history, with each issue routed to a fix.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). It is one of the core plugins, and no
other plugin installs it as a dependency. Some parts need more installed:

| Needs                                                 | For                                                                                    | Without it                                                                                                             |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `git`                                                 | Every skill. The workspace sync hook needs git 2.27 or later                           | The skills cannot run                                                                                                  |
| The GitHub CLI (`gh`), signed in with `gh auth login` | `pull-request`, `release`, replying on PR threads, PR times in a retro, PR checkpoints | `pull-request` can still merge a local branch, review replies come back as text, and the retro uses merge commits only |
| `python3` on PATH                                     | Every hook, and the changelog check in `update-changelog`                              | The hooks fail open. The changelog is checked by hand                                                                  |
| [uv](https://docs.astral.sh/uv/)                      | Checking and rendering a saved code review or retro                                    | The file is saved unchecked, and the agent says its Markdown was not rendered                                          |

## Skills

| Skill                     | Say or type                                                                                                          | What it does                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit`                  | Loads by itself when a commit is made or its message written, `/ceh-git-workflow:commit`                             | Writes the message as a Conventional Commit: type and scope, subject line, body, and footers for breaking changes and issue references.                                                                                                                                                                                                                                                |
| `pull-request`            | "open a PR", "merge it", "land this", `/ceh-git-workflow:pull-request`                                               | Takes a branch into `main`: changelog, commit, PR, merge and cleanup. It writes the PR body and runs a check before the merge. It can also merge a local branch with no PR.                                                                                                                                                                                                            |
| `release`                 | "cut a release", "bump the version", "hotfix", `/ceh-git-workflow:release [version]`                                 | Ships a version: bump, changelog, PR, merge, tag and GitHub release. It also covers a tag only and the hotfix path.                                                                                                                                                                                                                                                                    |
| `write-code-review`       | "review this PR", "is this ready to approve", `/ceh-git-workflow:write-code-review`                                  | Reviews a PR or someone else's diff: what to read first, blocking versus advisory comments, and a verdict. A linked spec is checked on its own and listed under Against the spec. Say "panel review" for the same review on two or three models, ranked by agreement, at several times the cost. Say "gate this PR" for two fresh reviewers who must both approve, up to three rounds. |
| `address-review-comments` | "address these review comments", "the reviewer said", `/ceh-git-workflow:address-review-comments [PR number or URL]` | Checks each comment on your change, from the PR or the branch's saved review file. It fixes what holds, pushes back with evidence on what does not, and replies to every thread. No reply agrees before quoting code or output, and a saved finding is ticked off with its resolution.                                                                                                 |
| `update-changelog`        | "update the changelog", "write release notes", `/ceh-git-workflow:update-changelog`                                  | Writes a `CHANGELOG.md` entry in Keep a Changelog format, as a versioned section or under `[Unreleased]`, and checks the file's versions and dates.                                                                                                                                                                                                                                    |
| `update-readme`           | "update the readme", "document this feature", `/ceh-git-workflow:update-readme`                                      | Brings `README.md` up to date after a change to how the project is installed, run or configured. It edits only the sections the change touches, and does nothing when nothing material changed.                                                                                                                                                                                        |
| `write-period-retro`      | "write a retro", "what did we ship this week", `/ceh-git-workflow:write-period-retro [since] [until]`                | Looks back over a period: what shipped, how work flowed, and at most three issues from git history, each routed to the skill that fixes it. Every number names the command it came from, and no line ranks a person.                                                                                                                                                                   |

## Agents

This plugin has no agents.

## Hooks

Four hooks run by themselves while the plugin is enabled, all on by default. [Settings](#settings)
turns them off.

| Hook                                        | What it does for you                                                                                                                         |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [Branch guard](#branch-guard)               | Stops a file edit while the default branch is checked out, and tells the agent to create a feature branch first.                             |
| [Workspace sync](#workspace-sync)           | Commits your `.agents_workspace` notes after every turn, and gives a git worktree the same workspace.                                        |
| [Skill-started guard](#skill-started-guard) | Stops a commit, a changelog, README or code review file edit until the skill that owns it has started, so its steps are not skipped.         |
| Review and retro check                      | Checks each saved code review or retro, renders its Markdown, and stops a hand edit to that Markdown, which the next render would overwrite. |

### Branch guard

The guard stops an edit when the file is in this session's repository and the checked-out branch
is the default branch (`origin/HEAD`, or `main` or `master`). It names the branch prefixes to use
(`feat/`, `fix/`, `chore/`, `docs/`, `test/`, `refactor/`). Uncommitted work carries over with
`git checkout -b`.

These pass:

- A git-ignored file, because it is never committed.
- A file outside a git work tree, or in another repository, whatever branch it is on.
- A detached `HEAD`, or a repository with no commit yet.
- A write through a shell command, such as `sed -i`. The guard covers the file tools only.

It fails open: unparseable input, a missing `git`, or a crashed interpreter allows the edit.

### Workspace sync

This hook acts only when the project's `.agents_workspace` folder is its own git repository. It
does nothing without one, on a detached `HEAD`, or in a bare repository.

- After every turn it commits the workspace's changes with the subject
  `chore(workspace): sync session <first 8 characters of the session id>`. To get a subject that names what was written, the agent
  commits the workspace itself before the turn ends.
- In a git worktree, or a subagent run with `isolation: "worktree"`, it gives the worktree the same
  workspace and merges it back when the session or subagent ends. A merge that fails is retried at
  the next session start, and the agent is told how to merge it by hand.
- After a `gh pr merge` that GitHub confirms, it adds an empty commit naming the PR, such as
  `chore(workspace): checkpoint source pr #123`. Merges made only in a browser are not recorded.
- Each commit ends with your `attribution.commit` line from the Claude Code settings.
- When the workspace branch tracks an upstream, it pushes the branch there in the background
  after it commits or merges. If the remote has moved on, it merges the remote first, but only
  when the workspace has no uncommitted files, and it leaves a conflict for you. If a push did
  not go through, the next session start tells the agent. Setting the upstream
  (`git -C .agents_workspace push -u origin <branch>`) turns this on, and
  `git -C .agents_workspace branch --unset-upstream` turns it off.
- It never stops a session.

A subagent's report can arrive before its workspace is merged, so read its records once its
completion notice arrives. An edit made during that merge can stay in a stash, which
`git -C .agents_workspace stash list` shows.

### Skill-started guard

| Call                                                   | Skill that must start first                      |
| ------------------------------------------------------ | ------------------------------------------------ |
| `git commit` in a shell command                        | `commit`                                         |
| An edit or write of a `CHANGELOG.md`                   | `update-changelog` or `release`                  |
| An edit or write of a `README.md`                      | `update-readme`                                  |
| A write under `.agents_workspace/product/review/code/` | `write-code-review` or `address-review-comments` |

A skill counts as started through the Skill tool or its slash command. A skill another skill only
names still has to be started. Files outside the session's project pass, and so does
`git commit` quoted inside another command, such as a `grep`. A subagent starts the skill itself.
The guard fails open.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                  | Default              | Effect                                                                                                                                                             |
| ------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CEH_BRANCH_GUARD`        | unset (guard on)     | `off` allows edits on the default branch, for when you asked to edit it in place                                                                                   |
| `CEH_SKILL_STARTED_GUARD` | unset (guard on)     | `off` allows a commit, or a changelog, README or code review file edit, before its skill started                                                                   |
| `CEH_ARTIFACT_CHECK`      | unset (check on)     | `off` turns the review and retro check off                                                                                                                         |
| `CEH_DISABLED_HOOKS`      | unset (all hooks on) | Comma-separated hook names to skip: `branch-guard`, `sync-agents-workspace`, `skill-started-guard`, `artifact-render-hook`, `generated-md-guard`                   |
| `CLAUDE_CONFIG_DIR`       | `~/.claude`          | Claude Code's own variable, not one this plugin adds. Workspace sync reads your `attribution.commit` line from `settings.json` there, after the project's settings |
| `GIT_SSH_COMMAND`         | unset                | Git's own variable. When unset, the workspace push uses `ssh -o BatchMode=yes`, so an SSH remote that needs a passphrase fails at once instead of waiting          |

## How it works

### One request, a few skills

`pull-request` and `release` each carry their full sequence. On every run they call only
`update-changelog`, plus `update-readme` when the change is user-facing. So a request such as
"commit, PR and merge" or "ship a release" loads two or three skills, not one per step.

## Not this plugin

- Language toolchains, coverage targets and package management: the stack plugins, such as
  `ceh-python-service` and `ceh-web-frontend`.
- Finding defects in a diff: Claude Code's built-in `/code-review`.

## Where its files live

The plugin saves code reviews in `.agents_workspace/product/review/code/` and retros in
`.agents_workspace/product/retro/`. A project with a root `product/` folder moves each file to the
same sub-path under `.agents_workspace/product/`, or names its own location in `CLAUDE.md`.
