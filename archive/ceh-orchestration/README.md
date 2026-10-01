# ceh-orchestration

Thin-orchestrator mode for cost-optimized, multi-step work. The main session
plans and delegates; cheap, isolated subagents do all the file I/O and execution.

The dominant cost lever in agentic work is **context isolation**, not model
choice — in a single loop every tool result accumulates in one window and is
re-billed every turn, so cost grows roughly quadratically with task length. This
plugin keeps the expensive orchestrator window lean and pushes the volume into
fresh, isolated workers whose raw output never returns to the parent.

## Skill

### `orchestrate`

Puts the session into thin-orchestrator mode: restate the goal, decompose into a
dependency-ordered plan, dispatch each subtask to a worker, and keep a compact
ledger of outcomes (never raw contents). The orchestrator does no file I/O
itself.

**Invoke:** `@"ceh-orchestration:orchestrate (agent)"`

**Auto-triggers on:** "orchestrate this", "act as orchestrator", "thin
orchestrator mode", "delegate this", "plan and delegate", "don't edit directly",
"fan this out to subagents", or any request to minimize token/context cost on a
big multi-file task.

Covers the cost model, hard no-I/O rules, the delegation map, model routing
(Opus → Sonnet → Haiku), spec discipline, the ranked cost levers, and why
subagents beat Agent Teams for a cost goal.

## Agents

The orchestrate skill dispatches these workers. Each runs in an isolated context
and returns only a terse final message.

For read-only exploration (locating code, mapping call sites, summarizing how
something works) the skill uses Claude Code's **built-in `Explore` agent** rather
than a custom one — it reads excerpts instead of whole files, takes a breadth
hint, and, unlike custom subagents, does **not** inherit `CLAUDE.md`, so it
carries the least context tax. This plugin therefore ships only the two workers
that have no built-in equivalent:

### `executor` (Sonnet)

Implements a single scoped task: code changes, edits, multi-step implementation.
Returns a files-changed list and a 1–2 line summary — no diffs or tool output.

**Invoke:** `@"ceh-orchestration:executor (agent)"`

### `verifier` (Haiku)

Checks an executor's output against explicit acceptance criteria and runs the
named checks. Returns PASS/FAIL plus a one-line reason — fixes nothing.

**Invoke:** `@"ceh-orchestration:verifier (agent)"`

> **Plugin-agent limitation:** Claude Code **ignores** the `permissionMode`,
> `hooks`, and `mcpServers` frontmatter fields on plugin subagents (security
> restriction). To grant edit/write permissions to `executor`, use session
> `permissions.allow` in `settings.json`, not agent frontmatter. See the
> [subagents docs](https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope).
>
> The env var `CLAUDE_CODE_SUBAGENT_MODEL` overrides every agent's `model:`
> field. Leave it unset to keep per-agent routing.

## Installation

```
/plugin install ceh-orchestration@ceh-plugins --scope user
```

Or manually in `~/.claude/settings.json`:

```json
{ "plugins": [{ "path": "~/agent-skills/plugins/ceh-orchestration" }] }
```
