# Runs index schema

`.agents_workspace/orchestration-lab/runs.md`, one row per orchestration-lab run, appended when the
run opens and updated when it closes, per `run-log.md` beside this file. A new index is a copy of
`../assets/runs-index.template.md`, relative to this file. The `schema: runs-index/v1` line stays
as written.

## Row

- **Started:** the run's start time, as in its `run.md`.
- **Project:** the repo name.
- **Strategy:** `plan-then-implement` or `orchestrate`.
- **Main**, **Worker:** the main and worker models, as in its `run.md`.
- **Outcome:** `running` while the run is open, then its Outcome.
- **Verdict:** empty while the run is open, then the user's verdict, or `not given`.
- **Folder:** the run folder's name.
