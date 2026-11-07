---
schema: plan/v2
generated_from: render-read-during-replace.yaml
generated_note: "Do not edit. artifact.py renders this file from render-read-during-replace.yaml: edit the YAML, then run artifact.py render."
title: A plan render survives reading the Markdown while another render replaces it
status: built
created: 2026-11-07
---

<!-- prettier-ignore-start -->

## Goal

On Windows, the three plan plugins' render hooks run at once after every plan edit, and the one
that reads the generated `.md` while another is renaming over it exits 2 with `PermissionError`
(`product/fixes/render-reads-markdown-while-another-render-replaces-it.md`). `write_atomic` in
`artifact.py` treats a refused read as a changed file and goes on to its rename, which already
retries, so every concurrent render ends with the same `.md` and exits 0. A regression fixture in
`validate.py` fails if the read ever goes unguarded again.

## Scope

**In:**

- `write_atomic` in every copy of `artifact.py`: an `OSError` from reading the target, a
  refused read or a missing file, counts as "the file differs", and the write goes on.
- A stdlib regression fixture in `tools/validate-plugins/checks/artifact_models.py` that loads
  `ceh-build-planning/scripts/artifact.py`, makes reading the target raise `PermissionError`,
  calls `write_atomic`, and fails unless the target then holds the new text.
- The fix record moved to `status: fixed` with its Fix and Tests sections, in the same commit.

**Out:**

- Running one render hook instead of three: Each plan plugin must render on its own when installed alone, and a cross-plugin lock adds
  shared state for a race the guarded read already makes harmless.
- Retrying the read in a loop: The rename after it already retries, and a reader that cannot open the file has nothing to
  compare, so going straight to the write is the shorter path to the same result.
- A race test in CI: It needs uv, three processes and many rounds, and still fails only one render in 30 to 60
  on Windows; the fixture forces the refused read deterministically instead.
- Guarding the `check` command's read of the `.md` (`artifact.py` line 145): `check` runs only from a skill step or `validate.py`, never from a hook. A PostToolUse hook
  finishes before the agent's next tool call starts, so no render is replacing the file
  while a `check` reads it.

## Design

- **The change:** `artifact.py` line 107, `if path.is_file() and path.read_text(encoding="utf-8") == text:`,
  becomes a `try:` that returns early when `path.read_text(encoding="utf-8") == text`, with
  `except OSError: pass`, inline in `write_atomic` and with no helper. Dropping `is_file()`
  removes a second call that touches the target, and a missing file raises
  `FileNotFoundError`, an `OSError`, so it still goes on to the write. Writing twice is
  harmless: the rename is atomic and every render writes the same text. The edited file is
  copied over its six other copies, which the `copies` check keeps identical.
- **The fixture:** In `artifact_models.py`, before the uv part so it runs without uv: load the script with
  `importlib.util.spec_from_file_location`, write a temp target holding old text, patch
  `Path.read_text` to raise `PermissionError` for that path only, and call
  `write_atomic(target, "new\\n")` inside `try:`, restoring the patch in `finally`. Any
  exception from the call, and a target that does not then read `new`, each call `fail`
  naming the script and "write_atomic does not survive a refused read", so the red run is a
  named failure, never a traceback that stops the later checks. `artifact.py` imports only the stdlib at the top, so loading it needs no
  pydantic.
- **Versions and changelog:** PATCH for `ceh-build-planning`, `ceh-build-from-plan` and `ceh-check-build-against-plan`, with
  their `CHANGELOG.md` row and `docs/PLUGIN_VERSIONS.md` rows, per
  `decision-version-levels.md` and `decision-changelog-sections.md`.

## Phases

### Phase 1: Guard the read and pin it with a fixture

- **Builds:** The fixture first, seen red on the current code; then the change in all seven copies, the fix
  record set to `fixed`, version bumps and the changelog entry.
- **Check:** Before the change, `python tools/validate-plugins/checks/artifact_models.py` fails naming the
  fixture. After it, `python tools/validate-plugins/validate.py` exits 0. Manual, Windows only,
  because the race depends on timing no CI runner reproduces: on a scratch copy of a plan, run
  60 rounds of changing its `title:` and starting three
  `uv run --script plugins/standalone/<plan plugin>/scripts/artifact.py render <copy>.yaml` at
  once, one per plan plugin, then `artifact.py check <copy>.yaml`; every render and every
  check exits 0.
- **Status:** done, Fixture red on the old code ("write_atomic does not survive a refused read"), green after;
  `validate.py` OK; manual race, 60 rounds of three renders and a check: 0 failures.

## Open

None

## Record

- 2026-11-07 Planned: status ready
- 2026-11-07 Reviewed: Revise first, 1 blocking (the fixture lets the refused read's PermissionError escape
  write_atomic and crash validate.py, so the red run is a traceback, not a fail naming the
  fixture, and the patch restore is skipped)
- 2026-11-07 PR: #218 https://github.com/cheneeheng/ceh-claude-code-library/pull/218
- 2026-11-07 Built Phase 1: fixture red then green, validate.py OK, race 0 failures in 60 rounds

<!-- prettier-ignore-end -->
