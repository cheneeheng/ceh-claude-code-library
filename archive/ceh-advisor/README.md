# ceh-advisor

Claude Code plugin providing a stronger-model second-opinion subagent — an owned replacement for
the native `/advisor`. The main session (whatever model it runs) consults the advisor at decision
points, failure loops, irreversible actions, and pre-completion gates. Triggering is two-layer:
soft (description-driven subagent routing) plus hard (deterministic hooks that ship with the
plugin), because soft triggering alone repeats the exact failure mode that motivates this plugin —
the model not recognizing it is at a decision point. The reviewer model is a single `model:` line
in the agent frontmatter; the point is ownership of the prompt and trigger logic, not vendor
independence.

## Agent

### `ceh-advisor`

Verdict-first senior reviewer (Opus, `xhigh` effort, Read/Grep/Glob on your code). States the
conclusion in line 1, justifies from files it read itself, deliberately steelmans the rejected
options before confirming the chosen one, and refuses to guess on thin context.

**Persistent memory.** The agent runs with `memory: local`, so it keeps notes across sessions at
`.claude/agent-memory-local/ceh-advisor/` (gitignored) — a past verdict, a diagnosis that turned
out wrong, a repo constraint that is not obvious from the code. Ask it to consult its memory
("check your memory for patterns you've seen here") and to update it once it has answered.

Enabling memory grants the agent Read, Write, and Edit so it can maintain those files, so it is
no longer tool-restricted to read-only. Its instructions confine writes to its own memory
directory; it does not edit your codebase. If you would rather keep it strictly read-only, drop
`memory: local` from `agents/ceh-advisor.md`. Memory also depends on auto memory being enabled —
with `autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` the field does nothing.

**Invoke:** `@"ceh-advisor:ceh-advisor (agent)"`

**Auto-triggers on:** an architectural fork about to be committed to; 2+ failed attempts at fixing
the same issue; an irreversible or destructive action about to run; a complex task about to be
declared complete.

**Handoff contract:** subagents spawn with a clean context window — the advisor does NOT see the
main conversation. Every invocation must include:

```
Situation: <what's being decided or what's failing>
Options considered: <list>
Leaning toward: <option> because <reason>
Relevant files: <paths>
```

An insufficient handoff gets back "missing: X, Y" instead of a guessed verdict. The contract is
encoded twice: in the agent `description` (visible at routing time) and in the agent body
(enforced at review time). If inline summaries start missing context, switch to a decision-log
file the main session appends to and the advisor reads — it already has `Read`, so that change is
prompt-only.

## Hooks

Hard-trigger backstops, wired by `hooks/hooks.json` and loaded automatically with the plugin.

| Script                                 | Event              | What it does                                                                                                                                                          |
| -------------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/ceh-advisor-guard.py`         | PreToolUse (Bash)  | Denies destructive commands (`rm -rf`, `git push --force`, `git reset --hard`, migrations, `terraform apply`, `kubectl delete`, ...) until a fresh advisor ack exists |
| `scripts/ceh-advisor-failure-watch.py` | PostToolUse (Bash) | At N consecutive failed bash calls, exits 2 to feed back: stop iterating, consult the advisor, challenge the diagnosis — any success resets the streak                |

**Requires `python3` on PATH.** Both hooks are Python (stdlib only, no packages) so they behave
identically on Linux, macOS, and Windows — the previous bash+`jq` versions needed a POSIX shell and
a `jq` binary that Windows does not ship. If `python3` is missing: `winget install Python.Python.3.12`
/ `brew install python` / `apt install python3`.

**Guard protocol:** deny → main session invokes `ceh-advisor` with a full handoff block covering
why the command is necessary and its blast radius → writes the advisor's one-line verdict into
`.claude/.ceh-advisor-ack` (doubles as an audit trail) → re-runs the command; a fresh ack unlocks
it. Deny + ack is used instead of `ask` because `ask` routes the decision to the human — the whole
point is that the model consults the advisor.

**Configuration:**

| Env var                      | Default                            | Purpose                                                 |
| ---------------------------- | ---------------------------------- | ------------------------------------------------------- |
| `CEH_ADVISOR_ACK_TTL`        | `900`                              | Seconds an ack stays valid                              |
| `CEH_ADVISOR_PATTERNS`       | `.claude/ceh-advisor-patterns.txt` | Extra destructive patterns, one extended regex per line |
| `CEH_ADVISOR_FAIL_THRESHOLD` | `3`                                | Consecutive failures before the watch fires             |

**Known limits (deliberate or documented):**

- Pattern matching is string-level, not shell-aware — a destructive pattern inside a quoted
  argument (`grep "TRUNCATE TABLE" docs/`) also denies. The backstop fails toward deny: a false
  positive costs one consult, a false negative costs the data.
- Honest-agent assumption: **no code ever writes the ack file** — step 3 of the protocol is carried
  out by the model itself, so the party being restrained is also the party issuing its own
  permission. Nothing stops it writing the ack without consulting. The guard is a backstop against
  _forgetting_, not an adversarial control.
- The ack is a blanket pass, not a per-command one: any destructive command is unlocked for the
  full TTL once one consult has happened. Lower `CEH_ADVISOR_ACK_TTL` if that window is too wide.
- Inside a **subagent** the guard still denies, but with a different message. Subagents have no
  `Task` tool, so "invoke ceh-advisor" is a dead end that leaves them stuck; they are told to stop
  and report to their caller instead, and explicitly told not to write the ack themselves. The
  guard is not skipped for subagents — that would let any destructive command through simply by
  delegating it. A fresh ack written by the caller _before_ delegating does unlock the subagent.
- Failure detection is heuristic (`is_error` plus common failure strings) because the PostToolUse
  payload shape has varied across Claude Code versions — extend the grep on false negatives.
- The guard **fails closed**. A deny is signalled the documented way — JSON on stdout with exit 0 —
  so it always carries a readable reason. An unparseable payload denies too, because a guard that
  cannot tell whether a command is destructive must not wave it through. `hooks.json` appends
  `|| exit 2` to the guard command so a missing `python3` (exit 127) or an unhandled crash (exit 1)
  _also_ blocks: Claude Code treats only exit 2 as blocking, so without that suffix the guard would
  fail open exactly when it is most broken. The trade-off is that a broken install blocks every
  destructive command until `python3` is on PATH — deliberate, and the reason it is documented here.
- The failure watch is advisory and **fails open**: on error it prints one line to stderr and exits
  1 (visible warning, nothing blocked) rather than a traceback on every bash call.
- `--force-with-lease` is **not** matched. It is still a history-rewriting push, just a safer one;
  add `git\s+push\s+(.*\s)?--force-with-lease` to `.claude/ceh-advisor-patterns.txt` if you want it
  gated too.
- No Stop hook by default — a pre-completion gate on `Stop` fires on _every_ stop, expensive and
  noisy. To add one yourself, put a prompt hook in your `settings.json` that blocks when the
  session involved high-stakes work and `ceh-advisor` was never consulted; trial it behind a flag
  file first.

## Testing

Smoke-test the hooks directly (`$PLUGIN` = this plugin's root, repo checkout or installed cache):

```bash
# Guard: destructive command, no ack -> deny JSON
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"},"session_id":"t1"}' \
  | python3 "$PLUGIN/scripts/ceh-advisor-guard.py"

# Guard: benign command -> silent allow (no output, exit 0)
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"},"session_id":"t1"}' \
  | python3 "$PLUGIN/scripts/ceh-advisor-guard.py"

# Guard: fresh ack -> allow with verdict in reason
mkdir -p .claude && echo "Go ahead — branch is already merged upstream." > .claude/.ceh-advisor-ack
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"},"session_id":"t1"}' \
  | python3 "$PLUGIN/scripts/ceh-advisor-guard.py"

# Failure watch: third consecutive failure -> exit 2 + stderr nudge
for i in 1 2 3; do
  echo '{"tool_name":"Bash","tool_input":{"command":"pytest"},"session_id":"t2","tool_response":{"is_error":true}}' \
    | python3 "$PLUGIN/scripts/ceh-advisor-failure-watch.py"; echo "run $i exit: $?"
done
```

Metrics to watch in live use:

- **Proactive vs. explicit-by-name invocation ratio** — mostly explicit means the soft trigger is
  under-firing and the hook layer needs widening.
- **Rubber-stamp rate** — the advisor agreeing with the "leaning toward" option >~80% of the time
  suggests the same-lab blind spot is live (reviewer shares training lineage with the requester).
- **Guard false positives** (benign commands matching patterns → tighten regexes) and
  **watch false negatives** (real failures not detected → extend the grep).

## Installation

```
/plugin install ceh-advisor@ceh-plugins --scope user
```

Or manually in `~/.claude/settings.json`:

```json
{ "plugins": [{ "path": "~/agent-skills/plugins/ceh-advisor" }] }
```

Restart Claude Code after installing or upgrading — hooks load at session start, no hot-swap.
Add `.claude/.ceh-advisor-ack` to your project's `.gitignore`.
