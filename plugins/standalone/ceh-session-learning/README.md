# ceh-session-learning

Turn one Claude Code session into something durable: a fix when the session went wrong, a skill
when it went right.

Your memory of a session, and the agent's, is a summary, and the summary is where a wrong turn
hides. `diagnose-session` reads the transcript itself. Four analysts run in parallel, one per lens
(instructions, tools, context, claims), and every finding cites a transcript line. The skill
re-reads the lines a conclusion rests on, classes each root cause, and names the file a fix goes
to.

A session that went well already holds the commands and flags that worked, their order, and every
correction you made along the way. `turn-session-into-skill` writes those into one `SKILL.md` in
the target repo's `.claude/skills/`, built from what actually ran instead of from an interview, so
the next session repeats the task without being told again.

Both load only when you ask, so other sessions pay nothing for them.

## Skills

| Skill                     | When it loads                                                   | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `diagnose-session`        | After a session went wrong, to find out why from its transcript | Finds the transcript, dispatches four `transcript-analyst` agents in parallel, verifies the cited lines, and routes each root cause to the skill that fixes it, acting on every route in this repo. On request, scrubs a shareable copy and has a fresh subagent audit the scrub. It's working if it names the transcript file first and every root cause cites a `<transcript>:<line>` and names a route. In-scope causes are saved, scrubbed, to `product/retros/`, the rest to `.agents_workspace/product/retros/`. |
| `turn-session-into-skill` | Right after a task is done, when you want it repeatable         | Recovers the steps that worked (from the transcript file when context was compacted), turns your corrections into rules and per-run values into arguments, writes one `SKILL.md`, and maps each step back to the session. Irreversible steps get a confirmation and user-only invocation.                                                                                                                                                                                                                              |

**Manual trigger:** `/ceh-session-learning:diagnose-session [session-id] [symptom]`, or say
`"diagnose this session"` / `"why did that session go wrong"`.
`/ceh-session-learning:turn-session-into-skill [skill-name]`, or say
`"turn what we just did into a skill"` / `"save this as a skill"`.

## Agents

| Agent                | Invoke                                         | When                                                                                                         |
| -------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `transcript-analyst` | Dispatched by `diagnose-session`, one per lens | Reads one transcript through one lens and returns at most 12 findings, each citing a line. Sonnet, read-only |

## Prerequisites

- The transcripts under `~/.claude/projects/` on the machine that ran the session. A session from
  another machine needs its `.jsonl` copied over first.
- `python3` lets the analysts print a condensed timeline of large transcripts. Without it they fall
  back to Grep.

## Not this plugin

- A mistake you already understand and want never to happen again:
  `ceh-every-session:prevent-repeat-mistake`, which `diagnose-session` routes an agent mistake to.
- A task you have not done yet, or one that needs approvals, resumption, or fan-out: use
  `ceh-workflow-builder`, which interviews the task and can emit a gated workflow. When the
  recovered steps need that shape and the builder is installed, `turn-session-into-skill` hands
  them over.
- Adding a skill to the ceh plugin repo itself.
