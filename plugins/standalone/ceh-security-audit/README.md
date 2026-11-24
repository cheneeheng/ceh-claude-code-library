# ceh-security-audit

Audit a whole codebase for weaknesses an attacker can reach, and get each one back as the attack it
enables. Claude Code's built-in `/security-review` checks pending changes only, and most
vulnerabilities sit in code that was merged long ago. This plugin covers the rest: it maps the
attack surface first, traces each entry point to the sinks it reaches, and rates every finding by
who can reach it and what it costs them.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin installs it as a
dependency. Some parts need more installed:

| Needs                                                              | For                                     | Without it                                                      |
| ------------------------------------------------------------------ | --------------------------------------- | --------------------------------------------------------------- |
| `git`                                                              | The search for secrets through history  | The audit runs, and lists that search as not run                |
| The ecosystem's audit tool (`pip-audit`, `npm audit`, `bun audit`) | The dependency check                    | The report lists the command to run                             |
| [uv](https://docs.astral.sh/uv/)                                   | Checking and rendering the saved report | The report is saved unchecked, and its Markdown is not rendered |

The audit tool sends your dependency list to an advisory database. So the dependency check runs
only when you ask for it or have already allowed network use. Otherwise the report lists the
command.

## Skills

| Skill                     | Say or type                                                                                                              | What it does                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `audit-codebase-security` | "security audit", "audit this repo for vulnerabilities", `/ceh-security-audit:audit-codebase-security [path or service]` | Maps entry points, trust boundaries, assets and attackers, then checks nine categories from access control to dependencies. It confirms each finding by quoting where input enters and the sink it reaches. The report opens with the attack surface, and every finding names its attacker. It fixes only on request, each fix with a test that fails first. |

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled, both on by default.
[Settings](#settings) turns them off.

| Hook                     | What it does for you                                                                                                                                                                |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Report check             | Checks the saved report each time it is written and renders its Markdown beside it. Errors go back to the agent to fix, and the Markdown stays as it was until the report is valid. |
| Generated Markdown guard | Stops a hand edit to the generated Markdown, and names the report file to edit instead.                                                                                             |

Both need uv. Without it, the agent is told once per session that the file went unchecked.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the report check and the generated Markdown guard off                |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

Nothing beyond the skills above.

## Not this plugin

- Changes not yet merged: Claude Code's built-in `/security-review`.
- Reviewing a PR: `ceh-git-workflow:write-code-review`, whose priority order includes security.
- Testing a deployed system: the skill proves findings locally and never touches a live host.

## Where its files live

Each audit is saved as a new file in `.agents_workspace/product/audit/security/`, with its
Markdown beside it, so a second audit keeps the first. The report stays in `.agents_workspace/`,
because a committed audit of an unfixed hole publishes it.
