# ceh-session-learning

Turn one Claude Code session into something durable: a fix when the session went wrong, a skill
when it went right. Your memory of a session, and the agent's, is a summary, and the summary is
where a wrong turn hides. So both skills work from the transcript itself, and both load only when
you ask, so other sessions pay nothing for them.

- **A session that went wrong.** `diagnose-session` has four analysts read the transcript in
  parallel, one per lens (instructions, tools, context, claims), and every finding cites a
  transcript line. The skill re-reads the lines a conclusion rests on, classes each root cause,
  and names the file a fix goes to.
- **A session that went right.** It already holds the commands and flags that worked, their order,
  and every correction you made along the way. `turn-session-into-skill` writes those into one
  `SKILL.md` in the target repo's `.claude/skills/`, built from what actually ran instead of from
  an interview, so the next session repeats the task without being told again.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Some parts need more installed:

| Needs                                       | For                                                      | Without it                                                                    |
| ------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| The transcripts under `~/.claude/projects/` | Both skills, on the machine that ran the session         | A session from another machine needs its `.jsonl` copied over first           |
| `python3` on PATH                           | A condensed timeline of large transcripts, and the hooks | The analysts fall back to Grep, and the hooks do nothing                      |
| [uv](https://docs.astral.sh/uv/)            | Checking the saved diagnosis and rendering its Markdown  | The YAML is saved unchecked, and the agent says the Markdown was not rendered |

uv installs pydantic and PyYAML on first use.

## Skills

| Skill                     | Say or type                                                                                                                | What it does                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `diagnose-session`        | "diagnose this session", "why did that session go wrong", `/ceh-session-learning:diagnose-session [session-id] [symptom]`  | Finds the transcript and names it first, dispatches four `transcript-analyst` agents in parallel, verifies the cited lines, and routes each root cause to the skill that fixes it, acting on every route in this repo. Every root cause cites a `<transcript>:<line>`, and all are saved, scrubbed, to one file. On request, it scrubs a shareable copy and has a fresh subagent audit the scrub. |
| `turn-session-into-skill` | "turn what we just did into a skill", "save this as a skill", `/ceh-session-learning:turn-session-into-skill [skill-name]` | Right after a task is done: recovers the steps that worked (from the transcript file when context was compacted), turns your corrections into rules and per-run values into arguments, writes one `SKILL.md`, and maps each step back to the session. Irreversible steps get a confirmation and user-only invocation.                                                                             |

## Agents

| Agent                | What it does                                                                                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `transcript-analyst` | Reads one transcript through one lens and returns at most 12 findings, each citing a line. `diagnose-session` dispatches one per lens. It runs on Sonnet and never edits. |

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Diagnosis check      | Checks a saved session diagnosis when it is written, and renders its readable Markdown copy. Without uv the agent is told once per session that the file went unchecked. |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite. The shareable copy is not generated, so its scrub edits pass.                        |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the diagnosis check and the generated-file guard off                 |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

Nothing beyond the skills above.

## Not this plugin

- A mistake you already understand and want never to happen again:
  `ceh-every-session:prevent-repeat-mistake`, which `diagnose-session` routes an agent mistake to.
- A task you have not done yet, or one that needs approvals, resumption, or fan-out: use
  `ceh-workflow-builder`, which interviews the task and can emit a gated workflow. When the
  recovered steps need that shape and the builder is installed, `turn-session-into-skill` hands
  them over.
- Adding a skill to the ceh plugin repo itself.

## Where its files live

`diagnose-session` saves its diagnosis in `.agents_workspace/product/retro/`, as a YAML file with
its Markdown copy and an optional `-shareable.md` copy beside it. `turn-session-into-skill` writes
to the target repo's `.claude/skills/`. A project that keeps product files in a root `product/`
folder moves each file to the same sub-path there, or names its own location in `CLAUDE.md`.
