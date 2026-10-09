# ceh-security-audit

Audit a whole codebase for weaknesses an attacker can reach, and get each one back as the attack it
enables.

Claude Code's built-in `/security-review` checks pending changes only, and most vulnerabilities
sit in code that was merged long ago. This plugin covers the rest: it maps the attack surface
first, traces each entry point to the sinks it reaches, and rates every finding by who can reach it
and what it costs them. The report stays in `.agents_workspace/`, because a committed audit of an
unfixed hole publishes it.

## Skills

| Skill                     | When it loads                                  | What it does                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `audit-codebase-security` | When the whole codebase needs a security audit | Maps entry points, trust boundaries, assets, and attackers, checks nine categories from access control to dependencies, confirms each finding by quoting where input enters and the sink it reaches, and fixes only on request, each fix with a failing-first test. It's working if the report opens with the attack surface and every finding names its attacker. |

**Manual trigger:** `/ceh-security-audit:audit-codebase-security [path or service]`, or say
`"security audit"` / `"audit this repo for vulnerabilities"`.

## Prerequisites

- `git`, for the secrets search through history.
- The ecosystem's audit tool (`pip-audit`, `npm audit`, `bun audit`) for the dependency check. It
  sends your dependency list to an advisory database, so it runs only when you ask for the
  dependency check or have already allowed network use. Otherwise the report lists the command.

## Not this plugin

- Changes not yet merged: Claude Code's built-in `/security-review`.
- Reviewing a PR: `ceh-git-workflow:code-review`, whose priority order includes security.
- Testing a deployed system: the skill proves findings locally and never touches a live host.
