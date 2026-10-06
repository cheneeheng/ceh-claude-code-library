# Model audit: ceh-core

- Date: 2026-10-06
- claude-code 2.1.291
- Edits applied: yes

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-core.doctor.md](ceh-core.doctor.md).

## Kept changes

None.

I fetched all seven pages and read the doctor report, both skills, `README.md`, `agents/bulk-reader.md` and the hook scripts. No edit was warranted, so I made none.

- **Report flags 1–4 (README thresholds and "never ask it to edit", undated measurement, `Do not editorialize`):** The report left all four alone. None is a missing file or command, and none is a contradiction between two instructions the model reads. No page backs a change, so they stay out.
- **`scripts/usage-limit-watch.py:181`, `do NOT write a handoff file`:** The general page does discourage bare emphasis, but its CAPS examples (`CRITICAL: You MUST use this tool when...`) come from the Opus 4.5 and 4.6 over-triggering discussion. The report reviewed this exact line and judged it acceptable. Per your tiebreak I follow the report, and the same message already says the calling session writes the handoff.
- **Verification rules in `skills/delegate-bulk-reads/SKILL.md`:** The Opus 5 page says to remove "include a final verification step" and "use a subagent to verify" instructions. Those target the model re-checking its own work. These rules check a Haiku worker's unseen output (anchors, `Not found / uncertain`, `Coverage`), so that quote does not apply and they stay.
- **Parallel-calls, progress-update, finish-the-task, autonomy and scope additions from the Fable 5.1, Sonnet 5.5 and Opus 5.5 pages:** None of these files shows the need those sections describe.
  - `usage-limit-handoff` is a deliberate stop protocol, so "keep working until done" would contradict it.
  - `delegate-bulk-reads` has no loop that issues independent calls.
- **Pinned file:** `agents/bulk-reader.md` is on your ignore list and was not judged.

## Pinned: `agents/bulk-reader.md`

No prompting guide exists for `haiku`, so it was not tuned.
