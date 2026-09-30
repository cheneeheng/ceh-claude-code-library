# ceh-coding-agent

A behavioral contract for coding agents: the rules that govern how an agent operates during a
session — what it may change, when it must stop, and how it logs decisions. The plugin loads the
contract automatically at session start, alongside the `write-less-code` minimalism skill.

It also carries the whole-repo passes an agent runs over code it did not write: `explain-codebase`,
the `repo-tree-mapper` agent, and `refactor-repo`.

It also owns the agent's context economy: `delegate-bulk-reads` and the cheap `bulk-reader`
agent push I/O-heavy reading onto a small model so file contents never reach the main context.

> The plan-driven workflow skills (`implement-from-plan`, `review-against-plan`) moved to the
> `ceh-plan-build-review` plugin, which bundles them with the planning skills.

## Skills

| Skill                      | When it loads                                                                                         | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agent-coding-contract`    | Every coding session (auto, via hook)                                                                 | The full behavioral contract — role, core rules, five-step workflow, stop conditions, decision logging.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `write-less-code`          | Every coding session (auto, via hook)                                                                 | The minimalism reflex — the ladder (YAGNI → stdlib → native → installed dep → one line), native-platform-first, the `// less-code:` shortcut convention. The positive half of the contract's minimal-change rules.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `shrink-diff`              | On demand — when a feature branch is functionally done and its diff should get smaller before review  | Retroactive minimalism — applies the write-less-code standard to the accumulated diff vs `main`, across all the commits and sessions that produced it: dedupe against existing code, delete dead weight, collapse over-built structure. Diff-scoped, with three narrow causes for touching unchanged code.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `refactor-repo`            | Manual only (`/refactor-repo`) — never auto-fires                                                     | Whole-codebase (or per-module) refactor campaign: read-only inventory, ranked proposal with payoff/risk/diff-size estimates, then apply only user-approved clusters on `refactor/` branches under a behavior-preservation gate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `usage-limit-handoff`      | When the usage-limit guard hook fires (5h or weekly window past threshold)                            | Stop-and-summarize protocol: close the current atomic step, start nothing new, write a durable handoff artifact to `.agents_workspace/handoff/` plus a line in the global `~/.claude/handoff/index.md`, end the turn. Subagents report upward instead of writing the artifact.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `explain-until-understood` | On demand — when someone in the session needs a subsystem, design, diff, or unfamiliar tool explained | How an explanation is built and what to do when it misses: assume the reader is new to the project and knows nothing about the subject, and say what floor you are building from; read the real code (never a design doc), foundations before the specific case, plain language (concept before name, every term of art defined at first use, project-local names included), verified output over described output, plain-ASCII pictures for structure and time (no box-drawing or arrow glyphs), a numbered walk of one ordinary case end to end, close on a transferable rule plus a self-test. Ships the escalation ladder — prose → steps → pictures → foundations — with the rule that a miss at pictures means a skipped foundation, not a missing detail; a reader lost on a _word_ is not on the ladder at all. Writes no files by default — `.agents_workspace/` scratch notes on request, and one narrow repo path for a subsystem explainer no other skill owns. |
| `explain-codebase`         | Manual only (`/explain-codebase`) — never auto-fires                                                  | Whole-repo orientation: what each component does, how they connect, and the key flows, written into a git-ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `delegate-bulk-reads`      | Before dispatching `bulk-reader`, and before acting on what it returns                                | The caller's half of the delegation. How to write the prompt so the answer is usable (one question per call, explicit paths, never ask it to edit), and the verification rules that apply afterwards: read the anchored lines before editing or reporting them, treat an unanchored bullet as unverified, and distrust a clean `Not found / uncertain` rather than lean on it — confirm coverage yourself, because every path sent owes a verdict in `Answer`. Carries the size floor (~400 lines, not "three or more files") and the rule that a "why" is worth splitting into several "wheres". Guard tuning lives below.                                                                                                                                                                                                                                                                                                                                                 |

**Manual triggers**

- `agent-coding-contract` — `/agent-coding-contract`, or say `"load the contract"` / `"agent contract"` / `"coding contract"`.
- `write-less-code` — `/write-less-code`, or say `"write less code"` / `"be lazy"` / `"simplest solution"` / `"yagni"`.
- `shrink-diff` — `/shrink-diff`, or say `"shrink the diff"` / `"consolidate the branch"` / `"can this diff be smaller"`.
- `refactor-repo` — `/refactor-repo` only (model auto-invocation is disabled by design).
- `usage-limit-handoff` — `/usage-limit-handoff`, or say `"wrap up the session"` / `"usage limit handoff"` / `"stop and summarize"`.
- `explain-until-understood` — `/explain-until-understood [what to explain]`, or ask for something to be explained until it makes sense.
- `explain-codebase` — `/explain-codebase`, or say `"explain this codebase"` / `"what does this repo do"`.
- `delegate-bulk-reads` — `/delegate-bulk-reads`, or say `"read these files and tell me..."` / `"where is X handled"` / `"I'm running low on context"`.

## Agents

| Agent              | When to use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bulk-reader`      | Read large or numerous files and return a compressed, line-anchored answer to one specific question. Runs on `haiku` with `Read`/`Grep`/`Glob` only — the model line is the entire cost saving, and the recall ceiling. Measured over 30 dispatches (the eval suite in [agent-skills](https://github.com/cheneeheng/agent-skills/tree/main/plugins/ceh-coding-agent/skills/delegate-bulk-reads/tests), not migrated): 100% recall on enumerative questions, 69% when the answer has to be assembled, which is why `delegate-bulk-reads` makes the caller confirm coverage. Read-only, never edits |
| `repo-tree-mapper` | Map or document a repository's structure into an annotated tree; auto-triggers on orientation requests                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

## Output style

| Output style                                             | When it applies                                                      | What it does                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CEH Coding Agent` (`output-styles/ceh-coding-agent.md`) | Every session while the plugin is enabled (`force-for-plugin: true`) | Response format and honesty rules: a Topic / Outcome / Status summary table for 2+ topics, code before prose, one complete thought per bullet, plain "I don't know", and reporting what was verified versus assumed. Sets `keep-coding-instructions: true`, so Claude Code's built-in engineering instructions stay in place. |

`force-for-plugin` overrides any `outputStyle` the user set, and if several enabled plugins force a
style, Claude Code uses the first one loaded. Output styles reach the main conversation and forks
only. Other subagents run their own system prompt, so rules that must hold there stay in
`CLAUDE.md` or the contract.

## How the skills auto-load

The plugin ships hooks (`hooks/hooks.json`) that activate automatically when the plugin is enabled —
no global `settings.json` change or env var required.

**At session start** — a `SessionStart` hook (`scripts/load-contract.sh`) injects a **mandatory**
directive to load `agent-coding-contract` before any other action, firing on `startup`, `resume`,
`clear`, and `compact` (so a fresh, resumed, or reset session has it loaded, and it is re-injected
after compaction).

**Every turn** — a `UserPromptSubmit` hook (`scripts/less-code-payload.sh`) re-injects a compact digest
of the `write-less-code` ladder before each prompt. This carries the minimalism reflex on every turn,
reliably from turn one; the full `write-less-code` skill loads on demand when non-trivial code is
actually being written.

**Every tool call** — a `PostToolUse` hook (`scripts/usage-limit-watch.py`) samples the account-wide
rate-limit percentage, taking whichever window is closest to its cap (the 5-hour and weekly windows
both count). When it crosses `CEH_USAGE_LIMIT_THRESHOLD` (default 90%), the hook tells the agent to
stop starting new work and run `usage-limit-handoff`; if ignored, it re-fires every 5 further
points of usage.

The reading is account-wide — claude.ai web, desktop, mobile and Claude Code draw from one pool —
and refreshes on every API round-trip, so sampling per tool call is fresh enough to stop
preemptively rather than after a 429. The hook reads the newest record across _all_ sessions and
projects, so a second Claude Code window does not leave a session acting on a stale number. Inside
a subagent it tells the subagent to stop and report upward instead of writing an artifact, since a
subagent sees only its own slice of the work.

> **Prerequisite for the usage-limit guard:** the hook reads the rate-limit data that a statusline
> export writes to `~/.claude/statusline/<project-dir>/<session_id>.jsonl` — a statusline script
> that appends its stdin JSON there (each line `{"session_id", "ts", "data": <payload>}`, with
> `:` and path separators in the project dir name replaced by `-`). Claude Code itself provides
> `rate_limits` only to the statusline, not to hooks, hence the relay. Without the export the guard
> warns once per session that it is inactive, rather than failing silently — everything else in the
> plugin works unchanged. Readings older than `CEH_USAGE_STALE_MINUTES` (default 15) are treated as
> unknown for the same reason: a stale low number reads as safety that is not there. A window whose
> `resets_at` has already passed is skipped regardless of the record's age — the reading predates
> the reset, so a high number there describes a window that no longer exists.
>
> The hook needs `python3` on PATH (stdlib only, no packages), which is what makes it behave the
> same on Linux, macOS, and Windows; it replaced a bash+`jq` version that needed a POSIX shell and
> a `jq` binary Windows does not ship. It is advisory, so it fails open: on error it prints one
> line to stderr and exits 1 (visible warning, nothing blocked).

**Before a read — opt-in** — two `PreToolUse` hooks (`scripts/bulk-read-guard.py` on `Read`,
`scripts/bulk-read-bash-guard.py` on `Bash`) deny whole-file reads of files at or above a line
threshold and point the agent at `delegate-bulk-reads` instead. Unlike every other hook here they
are **inert unless `BULK_READER_MIN_LINES` is set**: this plugin loads in most sessions, and
denying reads by default is not a decision to make on a user's behalf.

Set it in `~/.claude/settings.json` to switch enforcement on:

```json
{ "env": { "BULK_READER_MIN_LINES": "350" } }
```

`350` is a reasonable starting value; below roughly 200 the delegation round-trip costs more than
it saves. `BULK_READER_ALLOW` takes colon-separated globs that are never blocked
(`*.lock:*/migrations/*`) on top of the built-in exclusions for lockfiles, minified assets, images
and archives. `BULK_READER_MIN_LINES=999999` suspends enforcement for a session without
unregistering the hooks — useful when doing the very things the skill warns against.

Targeted reads always pass: `Read` with `offset`/`limit`, piped or redirected bash
(`cat f | grep x`), and `head`/`tail` that genuinely print a small window. The bash guard resolves
that window against the real file rather than reading the bare integer, so `tail -n +1` (an offset
— it prints the whole file) is blocked while `tail -n +400` on a 500-line file is not, and `-c`
is measured in bytes. Several files in one command are summed: `cat a b c` costs their total.
Both guards need `python3` on PATH
(stdlib only) and fail open — unparseable input, a binary file, a missing path, or a crashed
interpreter allows the read through, because a guard that blocked work on its own bugs would cost
more than it saves.

Three limits are worth knowing before turning enforcement on. The guards are one-directional: they
make delegation happen, but nothing verifies the summary was right, which is why the skill requires
spot-checking anchors before acting. They are a nudge with teeth rather than a sandbox — `sed -n`,
`awk`, `python -c open(...)` and an editor all still read files, and the bash guard covers only the
common dumps. And a delegation is a full subagent turn, so on small files it is strictly worse than
reading directly; that is what the threshold exists to prevent.

**Prior art.** The read-delegation design here follows
[Portal by Spotify cut my Claude Code token usage by 90%](https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90)
(Dimitri Mazmanov, September 2026), which pairs a `bulk-reader` worker on a cheaper model with a
hook that intercepts reads over 350 lines. This plugin keeps the shape and the threshold but not
the infrastructure: the worker is a plain Claude Code subagent rather than a hosted runtime, and
the guards are stdlib Python hooks with no service behind them. The 90% figure is theirs and is not
reproduced here — the eval suite left behind in
[agent-skills](https://github.com/cheneeheng/agent-skills/tree/main/plugins/ceh-coding-agent/skills/delegate-bulk-reads/tests) measures this implementation against its own
corpus and finds roughly 78% saved on enumerative questions, where recall is perfect, and 62% on
reasoning ones, where about three facts in ten go missing.

## What the contract enforces

The `agent-coding-contract` skill is the single source of truth. In short, it requires the agent to:

- **Run Autonomous Mode** — on routine ambiguity, decide the conservative option, log it, and
  continue; stop only for the hard cases (unresolvable conflicts, repo state contradicting
  instructions, risk of data loss, inconsistent partial failure).
- **Follow the five-step workflow** — Understand → Confirm scope → Apply changes → Validate →
  Summarize. Quick checks scoped to the edit are always allowed; test suites, builds, and
  state-changing commands run only when explicitly requested.
- **Make minimal, authorized changes** — localized diffs, no unsolicited refactors, touch only what
  is in scope, never claim work was done that wasn't.
- **Log decisions made under ambiguity** to `.agents_workspace/DECISION_LOG.md` (default path;
  override it via your project `CLAUDE.md`). See the skill for the entry format and when to log.

Refer to the skill for the authoritative wording — this section is a summary and is not the contract
itself.
