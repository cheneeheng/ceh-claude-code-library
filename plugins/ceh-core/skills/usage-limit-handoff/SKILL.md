---
name: usage-limit-handoff
description: >-
  Stop-and-summarize protocol for when the account usage limit is nearly exhausted. Load immediately
  when a hook or system message reports that usage crossed the wrap-up threshold ("ceh usage-limit
  guard"), and whenever the user says "usage limit handoff", "wrap up the session", "we're near the
  usage limit", "stop and summarize", or "hand off before the limit". Defines how to stop cleanly:
  finish only the current atomic step, start nothing new, write a durable handoff artifact recording
  completed vs open work, and end the turn. Not for ordinary end-of-task summaries (the contract's
  Summarize step covers those) or general session summaries without a limit trigger.
---

# Usage limit handoff

The usage window is nearly exhausted. The goal is no longer finishing the task — it is stopping
at a clean boundary so the work can resume without archaeology. A hard limit cut-off mid-edit
loses more than the remaining budget can save.

The point of stopping _before_ the limit is that everything needed for a good handoff is still
in context. Reconstructing it afterwards from a transcript costs far more than writing it now.

## Procedure

### If you are a subagent

Do **not** write a handoff artifact. You see only your slice of the work, and your final report
goes to the calling session rather than the user. Finish the current atomic step, then stop and
report — as your final message — the guard trip, what you completed, and what remains. The main
session owns the artifact.

The rest of this protocol applies to the main session.

### Main session

Execute these steps in order, then end the turn.

1. **Close the current atomic step — start nothing new.** Complete the single edit, command, or
   file write in flight so nothing is half-applied; if it cannot be completed within a few tool
   calls, revert it instead and record it as open. Do not begin the next subtask, launch
   subagents or background tasks, or run validation that was not already in flight.
2. **Secure unsaved state.** If uncommitted changes exist and committing was already authorized,
   commit them; otherwise leave the working tree as-is and describe its state in the artifact.
   Never commit or stash unprompted just because the session is ending.
3. **Write the handoff artifact** to
   `.agents_workspace/handoff/HANDOFF-<YYYYMMDD-HHMM>-<session-id-prefix>.md`
   (format below). Create the directory if needed. Take the session id prefix from the guard
   message and the timestamp from a single `date` call — do not guess either.
4. **Append one line to the global index** at `~/.claude/handoff/index.md`, creating it if
   absent:
   `- <YYYY-MM-DD HH:MM> — <cwd> — <branch> — <one-line state> — <artifact path>`
   This is what makes the work findable days later without remembering which repo it was in.
5. **Report the same content as your final message**, so it is visible without opening the file.
6. **End the turn.** Do not resume work in this session unless the user explicitly says to
   continue — they may prefer to wait for the window reset reported by the guard message.

## Rules

- The trigger is the `usage-limit-watch.py` PostToolUse hook in this plugin. It fires at
  `CEH_USAGE_LIMIT_THRESHOLD` (default 90%) against whichever window is closest to its cap —
  the 5-hour and weekly windows both trigger it — and re-fires every 5 points above that. A
  repeat warning means the first one was ignored; stop immediately.
- The quota reading is account-wide: claude.ai web, desktop, mobile and Claude Code all draw
  from the same pool, so usage can climb without this session doing anything.
- If the guard fires while mid-handoff, ignore it: the protocol is already running.
- Resume by reading the artifact in a fresh session rather than replaying the old one with
  `--resume` — the replay spends the quota that just reset.

## Output

```markdown
# Usage-limit handoff — <YYYY-MM-DD HH:MM>

**Window:** <name> at N%, resets at HH:MM
**Repo / branch:** <path> / <branch>
**Session:** <session-id-prefix>

**Goal** — what this session set out to do:

- <one or two lines>

**Done** — completed and in what state (validated / not validated):

- <item — files touched, what was verified>

**In flight** — the step that was closed or reverted at the cut:

- <state of the working tree, anything half-planned>

**Open** — remaining work, ordered; first item is the next actionable step:

1. <next concrete step, specific enough to execute cold>
2. <...>

**Decisions pending** — forks the user still has to resolve, if any.

**Resume with:** <one line: branch name, command to run, or file to open first>
```

Keep it factual and specific: file paths, branch names, exact commands. The reader is a future
session with none of this context. Keep it short enough to read in full on resume — a bounded
snapshot, never a log.
