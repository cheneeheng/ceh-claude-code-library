# ceh-core

Standards that hold however Claude Code is used — coding, writing, research, or ops. Nothing here
assumes a repository, code, or a specific activity; that is the admission test for this plugin.

Today it carries two session-protection concerns: `usage-limit-handoff` stops a session cleanly
before the account usage limit cuts it off, and `delegate-bulk-reads` with the cheap `bulk-reader`
agent pushes I/O-heavy reading onto a small model so file contents never reach the main context.

## Skills

| Skill                 | When it loads                                                              | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `usage-limit-handoff` | When the usage-limit guard hook fires (5h or weekly window past threshold) | Stop-and-summarize protocol: close the current atomic step, start nothing new, write a durable handoff artifact to `.agents_workspace/handoff/` plus a line in the global `~/.claude/handoff/index.md`, end the turn. Subagents report upward instead of writing the artifact.                                                                                                                                                                                                                                                                                                                                              |
| `delegate-bulk-reads` | Before dispatching `bulk-reader`, and before acting on what it returns     | The caller's half of the delegation. How to write the prompt so the answer is usable (one question per call, explicit paths, never ask it to edit), and the verification rules that apply afterwards: read the anchored lines before editing or reporting them, treat an unanchored bullet as unverified, and distrust a clean `Not found / uncertain` rather than lean on it — confirm coverage yourself, because every path sent owes a verdict in `Answer`. Carries the size floor (~400 lines, not "three or more files") and the rule that a "why" is worth splitting into several "wheres". Guard tuning lives below. |

**Manual triggers**

- `usage-limit-handoff` — `/usage-limit-handoff`, or say `"wrap up the session"` / `"usage limit handoff"` / `"stop and summarize"`.
- `delegate-bulk-reads` — `/delegate-bulk-reads`, or say `"read these files and tell me..."` / `"where is X handled"` / `"I'm running low on context"`.

## Agents

| Agent         | When to use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bulk-reader` | Read large or numerous files and return a compressed, line-anchored answer to one specific question. Runs on `haiku` with `Read`/`Grep`/`Glob` only — the model line is the entire cost saving, and the recall ceiling. Measured over 30 dispatches (the eval suite in [agent-skills](https://github.com/cheneeheng/agent-skills/tree/main/plugins/ceh-coding-agent/skills/delegate-bulk-reads/tests), not migrated): 100% recall on enumerative questions, 69% when the answer has to be assembled, which is why `delegate-bulk-reads` makes the caller confirm coverage. Read-only, never edits |

## Hooks

The plugin ships hooks (`hooks/hooks.json`) that activate automatically when the plugin is enabled.
Each hook script is stdlib-only Python, needs `python3` on PATH, and fails open: a hook that blocked
work on its own bugs would cost more than it saves. One subsection per guard below.

| Guard                                   | Event                         | Script(s)                                       | Default |
| --------------------------------------- | ----------------------------- | ----------------------------------------------- | ------- |
| [Usage-limit guard](#usage-limit-guard) | `PostToolUse` (every tool)    | `usage-limit-watch.py`                          | on      |
| [Bulk-read guards](#bulk-read-guards)   | `PreToolUse` (`Read`, `Bash`) | `bulk-read-guard.py`, `bulk-read-bash-guard.py` | opt-in  |

### Usage-limit guard

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

### Bulk-read guards

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
