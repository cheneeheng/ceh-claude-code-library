# ceh-session-diagnosis

Find why a Claude Code session went wrong from its transcript, and turn each cause into a fix.

Your memory of a session, and the agent's, is a summary, and the summary is where a wrong turn
hides. This plugin reads the transcript itself. Four analysts run in parallel, one per lens
(instructions, tools, context, claims), and every finding cites a transcript line. The skill
re-reads the lines a conclusion rests on, classes each root cause, and names the file a fix goes
to. It loads only when you ask, so sessions that go fine pay nothing for it.

## Skills

| Skill              | When it loads                                                   | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------ | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `diagnose-session` | After a session went wrong, to find out why from its transcript | Finds the transcript, dispatches four `transcript-analyst` agents in parallel, verifies the cited lines, and routes each root cause to the skill that fixes it, acting on every route in this repo. On request, scrubs a shareable copy and has a fresh subagent audit the scrub. It's working if it names the transcript file first and every root cause cites a `<transcript>:<line>` and names a route. In-scope causes are saved, scrubbed, to `product/retros/`, the rest to `.agents_workspace/product/retros/`. |

**Manual trigger:** `/ceh-session-diagnosis:diagnose-session [session-id] [symptom]`, or say
`"diagnose this session"` / `"why did that session go wrong"`.

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

- A session that worked and should be repeatable: `ceh-session-to-skill`.
- A mistake you already understand and want never to happen again:
  `ceh-every-session:prevent-repeat-mistake`, which this skill routes an agent mistake to.
