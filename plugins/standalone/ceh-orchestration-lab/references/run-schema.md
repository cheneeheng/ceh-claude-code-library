# Run schema

The `run.md` every orchestration-lab run writes in its run folder,
`.agents_workspace/orchestration-lab/<stamp>_<session id>/`, opened and closed per `run-log.md`
beside this file. A new run is a copy of `../assets/run.template.md`, relative to this file. The
`schema: run/v1` line stays as written.

## Title

The task in a few words.

## Field table

Filled when the run opens:

- **Started:** the start time, ISO-8601 in UTC.
- **Session:** the session id.
- **Transcript:** the path of `~/.claude/projects/*/<session id>.jsonl`.
- **Project:** the repo name and the project root.
- **Strategy:** `plan-then-implement` or `orchestrate`.
- **Main model:** the model id this session runs on.
- **Worker model:** `haiku`, `sonnet`, `opus`, or `fable`.
- **`CLAUDE_CODE_SUBAGENT_MODEL`:** `unset`, or its value.
- **Base:** the base SHA, then `clean`, or `dirty (see base.diff)`.

Left empty until the run closes:

- **Finished:** the close time.
- **End:** the end SHA.
- **Outcome:** `solved`, `partial`, `failed`, or `abandoned`, plus one line on why.
- **Dispatches:** the ledger's count line.
- **User interventions:** each time the user steered the work, with what they said.
- **Verdict:** the user's 1 to 5 rating and optional note, or `not given`.

## Sections

- **Task:** the user's request, verbatim.
- **Plan or briefs:** filled by the skill: the plan, or the briefs it dispatched, plus any change
  to the plan or split mid-run, with its reason.
- **Ledger:** filled at close with the output of `dispatch_ledger.py`.
- **Token usage:** filled at close with the table from `token_usage.py`.
- **Notes:** untracked files at the base and the end, and anything else the transcript cannot
  show.
