# Run log

Every run of an orchestration-lab skill leaves one folder in the target project, so the user can
compare strategies across real tasks later and turn a run's base commit into a benchmark fixture.
The log is the point of the experiment: a run without it is lost data.

All paths below are relative to the target project root. `<session id>` and `<plugin root>` are
the values the calling skill states at its top: this file is read, not loaded, so Claude Code
substitutes no variables in it.

## Open the run

Do this before reading any code for the task.

1. Get the start time in UTC twice: `<stamp>` as `YYYYMMDD-HHMMSS` for the folder name and
   `<started>` as ISO-8601 (`2026-10-09T14:02:11Z`) for the table and the token report.
2. Create `.agents_workspace/orchestration-lab/<stamp>_<session id>/`, the run folder.
3. Record the base state: `git rev-parse HEAD` is the base SHA. If `git status --porcelain` lists
   anything, the base is dirty: save `git diff HEAD` to `base.diff` in the run folder and list the
   untracked files under Notes, because the SHA alone no longer reproduces the starting tree.
4. Find the transcript: the file matching `~/.claude/projects/*/<session id>.jsonl`.
5. Check whether `CLAUDE_CODE_SUBAGENT_MODEL` is set. It overrides the model of every subagent
   dispatch, so a set value makes the run's worker model meaningless. Record it either way.
6. Write `run.md` from the template below, filling every field known now.
7. Append one row to `.agents_workspace/orchestration-lab/runs.md`, creating it with the header
   below if missing, with Outcome `running`.

## `run.md` template

```markdown
# <task in a few words>

| Field                        | Value                                 |
| ---------------------------- | ------------------------------------- |
| Started                      | <started>                             |
| Finished                     |                                       |
| Session                      | <session id>                          |
| Transcript                   | <transcript path>                     |
| Project                      | <repo name> (<project root>)          |
| Strategy                     | <plan-then-implement or orchestrate>  |
| Main model                   | <model id this session runs on>       |
| Worker model                 | <haiku, sonnet, opus or fable>        |
| `CLAUDE_CODE_SUBAGENT_MODEL` | <unset or its value>                  |
| Base                         | <sha>, clean or dirty (see base.diff) |
| End                          |                                       |
| Outcome                      |                                       |
| Dispatches                   |                                       |
| User interventions           |                                       |
| Verdict                      |                                       |

## Task

<the user's request, verbatim>

## Plan or briefs

<the skill fills this section>

## Ledger

<one line per dispatch: time, worker, what it was asked, what it reported>

## Token usage

## Notes
```

## `runs.md` header

```markdown
| Started | Project | Strategy | Main | Worker | Outcome | Verdict | Folder |
| ------- | ------- | -------- | ---- | ------ | ------- | ------- | ------ |
```

## While the run is open

- Add a Ledger line after every dispatch and every report, at the time it happens. A ledger
  rebuilt at the end from memory loses the failures.
- Count every time the user steers the work (a correction, a hint, a "stop") as a user
  intervention, and note what they said. An intervention means the strategy did not carry the
  task alone, which is exactly what the comparison needs to know.

## Close the run

Close the run when the skill's procedure ends, whether the task succeeded, failed, or was
abandoned.

1. Record the end state: `git rev-parse HEAD` is the end SHA. Save `git diff <base sha>` to
   `final.diff` in the run folder and list new untracked files under Notes. Do not commit: the
   user decides what lands.
2. Run `python <plugin root>/scripts/token_usage.py <session id> --since <started>` and paste its table under Token usage. It covers this session and its subagents from the
   start of the run. If it fails, write the error there instead.
3. Fill Finished, End, Outcome (`solved`, `partial`, `failed`, or `abandoned`, plus one line on
   why), Dispatches (the number of worker dispatches and resumes), and User interventions.
4. Ask the user with `AskUserQuestion` for a verdict from 1 (worse than doing it without the
   skill) to 5 (clearly better), with an optional note. Write it to Verdict. If they skip it,
   write `not given`.
5. Update the run's row in `runs.md` with Outcome and Verdict.
6. Tell the user the run folder path and the outcome in two lines.
