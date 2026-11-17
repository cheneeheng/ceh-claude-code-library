---
name: audit-codebase-security
description: >-
  Load this skill when a whole codebase, not one diff, needs a security audit: attack surface, entry
  points traced to sinks, each exploitable finding with severity and fix. Trigger on "security
  audit", "is this codebase secure". Not for pending changes (use the built-in /security-review).
argument-hint: "[path or service]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Needs git for the secrets search through history. The dependency check needs the ecosystem's
  audit tool (pip-audit, npm audit, bun audit) and network access. Without them the audit runs and
  lists those checks as not run. Checking and rendering the report's YAML needs uv; without it the
  report is saved unchecked and its Markdown is not rendered.
license: Apache-2.0
---

# Audit Codebase Security

Audit everything already in the codebase for weaknesses an attacker can reach, and report each
one as the attack it enables. Claude Code's built-in `/security-review` checks pending changes
only, and most vulnerabilities are in code that was merged long ago. Done means every entry point
is traced, every category below is checked or listed as skipped with a reason, and the report is
saved.

## Procedure

1. **Map the attack surface before reading for bugs.** List the entry points (HTTP routes, CLI
   arguments, queue consumers, webhooks, file uploads and parsers, jobs that read external data),
   the trust boundaries where outside data enters, the assets (credentials, personal data, money,
   admin actions), and the attackers who can reach each entry point (anonymous, signed-in user,
   another tenant, an operator). Severity only means something against an asset and an attacker
   who can reach it.
2. **Trace each entry point to its sinks**: queries, shell commands, file paths, HTML and
   templates, outbound requests, deserializers, `eval`. Request every search and file read that does not depend on another's result in the same turn. Check each category, and name the ones that
   do not apply:

   | Category         | Look for                                                                                                            |
   | ---------------- | ------------------------------------------------------------------------------------------------------------------- |
   | Access control   | A route with no auth, an object fetched by id with no owner check, a role checked only in the UI, tenant from input |
   | Injection        | SQL or shell built from strings, a file path from input with no containment check, unescaped HTML                   |
   | Secrets          | Credentials in code, config, tests, or git history (`git log -p -S '<pattern>'`), tokens written to logs            |
   | Outbound         | A server-side fetch of a URL from input (SSRF), an open redirect                                                    |
   | Parsing          | Unsafe deserialization (`pickle`, `yaml.load`), XML external entities, archive path traversal, unbounded uploads    |
   | Crypto, sessions | Fast hashes for passwords, `random` for tokens, unverified JWTs, cookies without `HttpOnly`, `Secure`, `SameSite`   |
   | Configuration    | Debug on in production config, CORS `*` with credentials, stack traces in error responses, default credentials      |
   | Resource limits  | No rate limit on login or costly endpoints, a regex with catastrophic backtracking on input                         |
   | Dependencies     | A pinned version with a published advisory                                                                          |

3. **Check dependencies only with consent to the network.** The audit tools send the dependency
   list to an advisory database, which is sending content to an external service. Run them when
   the user asked for the dependency check or network use is already authorized. Otherwise put the
   exact command under Not checked.
4. **Fan out on a large surface.** With more than one service, or more than about fifty entry
   points, write the surface map to the report's `attack_surface` first, then dispatch background subagents in
   parallel, one per group of categories, each with the report path and its categories. Merge by
   `path:line`, and re-read every quoted line before it becomes a finding.
5. **Confirm each finding** by quoting both ends: where the attacker's input enters and the sink
   it reaches, with every step between that could stop it. Rate **severity** (critical, high,
   medium, low) from impact and reachability, and **confidence**: confirmed (traced end to end, or
   proven by a local test) or likely. A finding you cannot trace goes under Possible, not in the
   table.
6. **Fix only on request.** When asked, fix confirmed critical and high findings first. Each fix
   lands with a test that fails before it and passes after. Leave the rest reported.

## Rules

- **Never copy a secret's value** into the report, a test, or the reply. Cite `path:line` and the
  kind of secret. Removing a committed secret from the code does not remove it from history, so
  the fix is rotating it, which is the owner's call: report it, never rotate it.
- **Prove locally, never live.** No request, scan, or exploit against a deployed system or a host
  the user does not run locally. A test or a local dev server is the proof.
- **Severity follows reachability.** An injection in a public route outranks the same injection in
  a script only an operator runs, so name the attacker in every finding.
- Save the report under `.agents_workspace/`, never in a committed path: a committed audit of an
  unfixed hole publishes it.

## Output

Save to `.agents_workspace/product/audit/security/<YYYYMMDD-HHMMSS>-<session-id>-security-audit.yaml`, so a
second audit keeps the first. Take `<YYYYMMDD-HHMMSS>` from one `date +%Y%m%d-%H%M%S` call and `<session-id>` from `${CLAUDE_SESSION_ID}`. Reply
with the counts by severity and the critical and high rows. The report fills
`assets/security-audit.template.yaml`, per the `security-audit/v2` section of
`references/security-audit-schema.md`. After the last edit, run
`uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py render <file>.yaml`, which writes the
`.md` beside it in the layout of `assets/security-audit.template.md`, and fix the YAML for each
error it lists. Before editing a saved report, run it with `check` and stop on exit 1 with its
errors. Never edit the generated `.md`. On exit 2 or 3, or without uv, say in the reply that the
report went unchecked and unrendered.

## Acting on findings

The saved report stays as it is: it records what the audit found, never what came of it. Act only
on the findings the user chooses in this session, and only on those this run did not already fix.
Choosing a finding is the request to fix it, and a fix made directly follows this skill's own rule
on commits. With no user to choose, as in a headless run or a
report-only subagent, route nothing: the report stands, and a calling agent does any routing.

| Finding is                               | Route                                                     |
| ---------------------------------------- | --------------------------------------------------------- |
| A bug in this repo's code or config      | `ceh-coding-conduct:find-root-cause`, writes a fix record |
| A feature or design change in this repo  | `ceh-build-plan:write-build-plan`                         |
| A rule for how work is done in this repo | `ceh-every-session:record-project-decisions`              |
| Anything else in this repo               | Fixed directly, with the check that proves it             |
| Outside this repo                        | Left for the user                                         |

Each chosen finding ends handed off, fixed, or dropped with a reason, and stays open only while it
waits on a user decision: one outside the repo, or a route whose plugin is not installed. A row in
a backlog file the repo names (in its README, `CLAUDE.md` or `AGENTS.md`) counts as handed off, and
an open finding gets one there too. Every plan, fix record, rule or backlog row names the audit
file and the finding as its source, the finding by its `id` where the format has one, else by its
`location`. The reply lists each chosen finding with where it went.
A committed secret always goes to the user, because rotating it is the owner's call.
