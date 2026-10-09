# ceh-orchestration-lab

**Experimental.** Try orchestration strategies on real coding tasks, and keep a record of each
run good enough to compare them later.

The synthetic benchmark in `.agents_workspace/experiments/orchestration/` could not tell the
strategies apart: `solo-haiku` solved every batch. This plugin moves the experiment into real
projects. You pick a strategy and a worker model per task, the skill runs it, and each run leaves
a folder with the base commit, the plan or briefs, every worker report, the token usage by model,
and your verdict. Once a pattern shows, a run's base commit and final diff become a fixture for a
controlled rerun.

It is in no scenario bundle and never will be while it is experimental.

## Skills

Both are user-invoked only, so a run is always a deliberate choice.

| Skill                 | When to run it                                  | What it does                                                                                                                                                        | It's working if                                                                                                              |
| --------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `plan-then-implement` | A task you want to try as one plan, one handoff | This session reads the code and writes a complete plan, one `implementer` on the worker model (default `sonnet`) carries it out, with at most one fix-up resume     | A run folder appears before any code is read, the plan is written into `run.md`, and this session never edits a project file |
| `orchestrate`         | A task you want to try as a supervised loop     | This session splits the work into briefs and reviews each report, `implementer` workers (default `haiku`) do every edit and every test run, resumed when incomplete | A run folder appears first, the Ledger gains a line per dispatch, and the token table shows most output on the worker model  |

**Manual trigger:** `/ceh-orchestration-lab:plan-then-implement [model] [task]` or
`/ceh-orchestration-lab:orchestrate [model] [task]`, where `[model]` is `haiku`, `sonnet`,
`opus`, or `fable`. Without a task, the skill takes your most recent request.

## Agents

| Agent         | Invoke                                         | When                                                                                                                                   |
| ------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `implementer` | Dispatched by both skills, `model` set per run | Carries out one brief, runs its check, and returns a report of at most 15 lines. Never commits or touches git state. Sonnet by default |

## Choosing a configuration

The benchmark had nine configurations. The skills cover the four that depend on how the work is
split. The other five are settings you choose before the task, with no skill at all:

| Benchmark config                 | How to run it on a real task                                                 |
| -------------------------------- | ---------------------------------------------------------------------------- |
| `solo-opus`, `-sonnet`, `-haiku` | `/model <model>`, then work as usual                                         |
| `sonnet+advisor-opus`            | `/model sonnet` with the Opus advisor on                                     |
| `haiku+advisor-opus`             | `/model haiku` with the Opus advisor on                                      |
| `plan-opus_impl-sonnet`          | `/model opus`, then `/ceh-orchestration-lab:plan-then-implement sonnet`      |
| `plan-opus_impl-haiku`           | `/model opus`, then `/ceh-orchestration-lab:plan-then-implement haiku`       |
| `opus+sub-haiku`                 | `/model opus`, then `/ceh-orchestration-lab:orchestrate haiku`               |
| `sonnet+advisor-opus+sub-haiku`  | `/model sonnet`, advisor on, then `/ceh-orchestration-lab:orchestrate haiku` |

The main model plans in both skills, so `/model` picks the planner or orchestrator. The token
report records whether an advisor was configured.

## The run log

Each run writes to the target project, not this repo:

```
.agents_workspace/orchestration-lab/
├── runs.md                                   # one row per run: started, project, strategy, models, outcome, verdict
└── 20261009-140211_<session-id>/
    ├── run.md                                # fields, task, plan or briefs, ledger, token usage, notes
    ├── base.diff                             # only when the tree was dirty at the start
    └── final.diff                            # git diff from the base commit at the end
```

The folder name sorts by start time and carries the session ID, which also names the transcript
at `~/.claude/projects/<project>/<session-id>.jsonl`. At the close of a run,
`scripts/token_usage.py` reads that transcript and its subagent transcripts and writes the token
counts by model, from the run's start time on, into `run.md`. You can run it by hand on any
session:

```bash
python scripts/token_usage.py <session-id> [--since 2026-10-09T14:02:11Z]
```

The skills never commit. If `.agents_workspace/` is not git-ignored in the target project, add it,
or the run folders show up as untracked files.

## Reading the results

- **Output share by model** is the delegation check. If an `orchestrate` run shows most output on
  the main model, delegation did not happen and the run says little about the strategy.
- **User interventions** count every time you had to steer. A strategy that solves tasks only with
  your help is not carrying them.
- **Verdict** is your 1 to 5 judgment against doing the task without the skill. It is the one
  field the transcript cannot give you.
- Real tasks differ, so compare strategies across many runs, not one pair. Use the base SHA and
  `final.diff` to rerun a telling task under every strategy with the benchmark harness.

## Prerequisites and caveats

- `git` and `python3` on `PATH`: the run log records commits and diffs, and the token report is a
  stdlib Python script. Without Python the run still completes, with the error in place of the
  token table.
- `CLAUDE_CODE_SUBAGENT_MODEL`, when set, overrides every subagent's model, so the worker model
  argument does nothing. The skills record its value in each run. Leave it unset while
  experimenting.
- The advisor's own calls may not appear in the transcript, so an advisor run's token table can
  understate Opus usage. The same accounting gap is open in the benchmark README.
- Plugin agents inherit your session's permissions. Put the session in `acceptEdits` or allow the
  edit tools, or every worker edit prompts you.

## Not this plugin

- A single subagent dispatch, or work where you do not want a run recorded: dispatch the agent
  directly.
- Choosing a model for normal work: use `/model`. This plugin exists to find out which choice is
  right, not to make it.
