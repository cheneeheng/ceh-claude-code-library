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
6. Write `run.md` from `../assets/run.template.md` (relative to this file), filling every field
   known now, per `run-schema.md` beside this file.
7. Append one row to `.agents_workspace/orchestration-lab/runs.md`, creating it as a copy of
   `../assets/runs-index.template.md` if missing, per `runs-index-schema.md` beside this file,
   with Outcome `running`.

## While the run is open

- Do not write Ledger lines as you go. Every edit to `run.md` is one more step for this session,
  and each step re-reads its whole context. The transcript already records every dispatch,
  resume, and report, failures included, and the close turns it into the Ledger.
- Write to `run.md` mid-run only what the transcript cannot show: a change to the plan or split,
  with its reason.
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
3. Run `python <plugin root>/scripts/dispatch_ledger.py <session id> --since <started>` and paste
   its output under Ledger: one line per dispatch, resume, report, and project edit this session
   made itself. If it fails, write the error there instead.
4. Fill Finished, End, Outcome (`solved`, `partial`, `failed`, or `abandoned`, plus one line on
   why), Dispatches (the ledger's count line), and User interventions.
5. Ask the user with `AskUserQuestion` for a verdict from 1 (worse than doing it without the
   skill) to 5 (clearly better), with an optional note. Write it to Verdict. If they skip it,
   write `not given`.
6. Update the run's row in `runs.md` with Outcome and Verdict.
7. Tell the user the run folder path and the outcome in two lines.
