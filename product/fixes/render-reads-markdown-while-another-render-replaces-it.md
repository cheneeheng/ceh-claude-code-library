---
schema: fix-record/v1
status: fixed
date: 2026-11-07
plan: product/plans/render-read-during-replace.md
---

# A plan render fails when another render is replacing the same Markdown on Windows

**Symptom:** three concurrent `uv run --script <plugin>/scripts/artifact.py render <plan>.yaml`, one
per plan plugin, as the three render hooks run after one edit, after the plan's title changed →
`artifact.py failed: PermissionError: [Errno 13] Permission denied: '<plan>.md'` (exit 2), 1 to 2
renders in 60, Windows 11. Seen live as the hook's "artifact.py exited 2" note on
`product/plans/registry-driven-copies.md`.

## Diagnosis

| Hypothesis                                                                 | Refuted by                                                  | Result                                                                                       |
| -------------------------------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| The rename in `write_atomic` runs out of its 10 retries                    | The traceback ends somewhere other than `os.replace`        | refuted: both failing tracebacks end at `write_atomic`, line 107, `path.read_text`           |
| The temp file collides between processes                                   | The error names the `.md`, not a `.tmp`                     | refuted: the error names `<plan>.md`                                                         |
| Something outside the renders (antivirus, an editor) holds the file        | One renderer alone, with the same changes, still fails      | refuted: one renderer, 120 rounds, 0 failures                                                |
| Reading the `.md` while another process's `os.replace` swaps it is refused | Concurrent renders fail even when nothing replaces the file | confirmed: traceback at line 107; three renders of an unchanged `.md`, 60 rounds, 0 failures |

**Cause:** `scripts/artifact.py:107` (`write_atomic`): the check that skips an unchanged file opens
the target with no retry, and on Windows opening a file while another process is replacing it is
refused with `PermissionError`. Each of the three plan plugins installs the same PostToolUse render
hook, so one edit starts three renders of the same `.md`, and the one that reads during another's
rename exits 2. The rename itself already retries.

**Prediction:** three concurrent renders where the title never changes, so no render replaces the
file → 0 failures in 60 rounds, seen. One renderer with a changing title → 0 failures in 120
rounds, seen.

## Fix

`write_atomic` reads the target inside `try` and treats any `OSError`, a refused read or a missing
file, as a changed file, so the write goes on to the rename, which already retries. Every render
writes the same text, so a second write is harmless. All seven copies of `artifact.py` changed
together.

**Tests:**

- `tools/validate-plugins/checks/artifact_models.py` `_survives_refused_read` — protects:
  `write_atomic` writes the new text when reading the target raises `PermissionError`;
  fails_when: the read goes unguarded again (red on the old code: "write_atomic does not survive a
  refused read"); why_new: no check exercised a render while another held the file, and the race
  needs Windows timing no CI runner gives.

**Unverified:** macOS and Linux, where `os.replace` does not block a reader, so the race is
inferred not to occur there. The manual race after the fix, 60 rounds of three renders and a
check, gave 0 failures, against 1 to 2 in 60 before. The fixture is the deterministic proof.
