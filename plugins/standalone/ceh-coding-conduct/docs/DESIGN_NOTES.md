# ceh-coding-conduct design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## Skills that moved out

> `explain-until-understood`, `explain-codebase`, and `document-architecture` moved to the
> `ceh-codebase-explanation` plugin: explaining code is an activity, not how an agent conducts
> itself while coding.
>
> `usage-limit-handoff`, `delegate-bulk-reads`, and the `bulk-reader` agent moved to the
> `ceh-every-session` plugin: they hold however Claude Code is used, not only when coding. The
> output style followed, rewritten without its coding-specific rules, as `CEH Every Session`.
>
> The plan-driven workflow skills moved out: planning and `implement-from-plan` to
> `ceh-build-plan`, and the check to `ceh-check-build-against-plan`.

## Hook wiring

The plugin ships hooks (`hooks/hooks.json`) that activate automatically when the plugin is enabled —
no global `settings.json` change or env var required.

**At session start** — a `SessionStart` hook (`scripts/load-contract.sh`) injects a **mandatory**
directive to load `agent-coding-contract` and `write-less-code` before any other action, then to pick the task skills
that match the request before reading any file. It fires on `startup`, `resume`, `clear`, and
`compact` (so a fresh, resumed, or reset session has it loaded, and it is re-injected after
compaction).

**Every turn** — a `UserPromptSubmit` hook (`scripts/inject-less-code-reminder.sh`) re-injects a compact digest
of the `write-less-code` ladder before each prompt. This carries the minimalism reflex on every turn,
reliably from turn one. It no longer asks the model to load the full skill "before non-trivial
logic": that conditional load was followed in 2 of 19 sessions, against 18 of 19 for the mandatory
contract load, so the full skill now loads at session start instead.

**When a subagent starts** — a `SubagentStart` hook runs the same two scripts, because neither
`SessionStart` nor `UserPromptSubmit` fires inside a subagent. An agent with a restricted tool list
has no Skill tool, so the directive points it at both skills' `SKILL.md` files to read instead. The
read-only agents are skipped: `Explore`, `Plan`, `bulk-reader`, `newcomer-simulator`,
`competitor-analyst`, `transcript-analyst`, and every agent whose name ends in `-reviewer`.

## Why each hook exists

Hooks are enforcement, so each one is kept on a failure that guidance alone did not prevent:

- **The contract loads first, unconditionally.** A directive to load the contract "when you write
  code" was tried, and the model never invoked it later in the session. The contract is model-only
  with a one-line description, so nothing else triggers it. The same directive sends the agent
  back to the skill listing: with only the contract named, two debugging sessions loaded it and no
  task skill, and read code for dozens of steps without `find-root-cause`.
- **The less-code reminder repeats every prompt.** Write-less-code is a standard that holds the
  whole session, not a moment, so no description fires it: an agent starting to write code does not
  stop to look for it. Loaded once, the ladder also drifted out of effect in long sessions and the
  agent over-built.

- **The fix record is checked on every write.** This one is kept on the user's choice, not on a
  failure: the fix record (`fix-record/v3`, `.agents_workspace/product/fix/<YYYYMMDD-HHMMSS>-<slug>.yaml`) is a handoff to
  `ceh-testing:test-a-bug-fix` and to later sessions, so it is checked whether or not
  `ceh-testing` is installed. See Fix record render and generated Markdown guard below.

## Fix record render and generated Markdown guard

A `fix-record/v3` record is `.agents_workspace/product/fix/<YYYYMMDD-HHMMSS>-<slug>.yaml`, with its `.md` rendered beside it. After
every Edit or Write to one, a `PostToolUse` hook (`scripts/artifact-render-hook.py`) checks the YAML
against its model through `uv` and renders the Markdown, or reports each error back to the agent
and leaves the Markdown as it was. A `PreToolUse` guard (`scripts/generated-md-guard.py`) denies a
direct edit to a generated Markdown file and names its YAML. `refactor-repo` saves its report as a
`.yaml` in `.agents_workspace/product/refactor/` (`refactor-report/v2`), which the same hook checks
and renders. Both run `python3` on every Edit or
Write and return at once for any other file, about 85 ms per edit for the two together, measured
once on Windows.

## Product folder history

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
