---
schema: plan/v2
generated_from: registry-driven-copies.yaml
generated_note: "Do not edit. artifact.py renders this file from registry-driven-copies.yaml: edit the YAML, then run artifact.py render."
title: The copies check compares the whole-file copies the registry declares
status: ready
created: 2026-11-07
---

<!-- prettier-ignore-start -->

## Goal

The `copies` check in `validate.py` stops guessing which files are copies from their path, and
reads them from `docs/CROSS_REFERENCES.md`, which already has to list every copy. It fails a
registered copy that differs from its canonical file (drift), a registered path that no longer
exists (stale), a whole-file row it cannot parse (malformed), and two byte-identical files at the
same path in different skill folders that no entry pairs (unregistered). Two unrelated files that
only share a name are left alone. The layout part of the check stays as it is.

## Scope

**In:**

- A registry reader in `checks/copies.py` that returns every registered whole-file pair, and
  fails a malformed whole-file row or Canonical paragraph.
- The four failures: drift, stale, malformed, unregistered, each naming the registry entry
  where one exists and every path involved.
- `docs/CROSS_REFERENCES.md` rewritten so every byte-checked row holds one full path and every
  canonical file it pairs with is named in full on its entry's Canonical line, with the Entry
  shape at the bottom showing the whole-file form.
- `tools/validate-plugins/README.md` and `plugins/CLAUDE.md` describe the new rule.

**Out:**

- The layout part of `copies.py`: Unchanged; it guards where files live, not which files are copies.
- Checking section copies inside a SKILL.md, README or agent: No byte check covers part of a file. Rows whose Section is a `§` stay hand-kept, as before.
- Whole-file rows with a declared divergence: A row whose Diverges cell is not `none`, such as the `ceh-python-library` env skill or the
  `ceh-testing` copy of `skill-started-guard.py`, differs on purpose and is not byte-checked.
- Plugin version bumps: Only `tools/` and `docs/` change, so no plugin's shipped content moves.

## Design

- **Which rows are byte-checked:** An entry is a `## ` section of `docs/CROSS_REFERENCES.md`, except `## Update protocol`. Lines
  inside fenced code blocks are skipped everywhere, so the Entry shape example is never read.
  A row inside an entry's Copy table is byte-checked when its Section cell starts with
  `whole file` (also `whole files`, `the whole file`, `entire file`) and its Diverges cell is
  exactly `none`. Its Copy cell must then hold exactly one backticked path starting with
  `plugins/` or `.claude/`, and nothing else in backticks; otherwise the row is malformed.
- **How a copy finds its canonical file:** An entry's canonical files are every backticked path starting with `plugins/` or `.claude/`
  in its `**Canonical:**` paragraph, which runs to the next blank line. A byte-checked row
  pairs with the canonical file of the same file name. No canonical file of that name, or more
  than one, is malformed, and so is an entry with byte-checked rows whose Canonical paragraph
  names no such path. The name match is scoped to one entry the author wrote, so it is a
  declaration, not a guess.
- **The four failures:** Each calls `fail(<path>, <message>)` with the entry heading in the message.

  - Drift: `fail(copy, "differs from <canonical> (<entry>)")`.
  - Stale: `fail("docs/CROSS_REFERENCES.md", "<entry>: <path> does not exist")`, for the
    copy path of a byte-checked row or the canonical path it pairs with. Canonical paths no
    byte-checked row pairs with are not checked, since section entries name SKILL.md files
    and relative paths such as `web/src/useAgent.ts`.
  - Malformed: `fail("docs/CROSS_REFERENCES.md", "<entry>: <the row or line>: <why>")`.
  - Unregistered: over files under each skill's `assets/`, `references/` and `scripts/`
    (skipping `__pycache__`), group by path relative to the skill folder. Two byte-identical
    files in one group that no registered pair links, directly or through a shared canonical
    file, fail with
    `fail(file, "identical to <other>; register the copy in docs/CROSS_REFERENCES.md")`,
    naming both files, since no entry exists to name.
    Files in one group that differ and are not registered pass: they are unrelated.
- **Where the code lives:** `tools/validate-plugins/checks/copies.py`, stdlib only like every check. A module-level
  `registered_pairs() -> list[tuple[str, Path, Path]]` returns (entry, canonical, copy) and
  calls `fail` for malformed rows, and `check()` runs the layout part, then drift, stale and
  unregistered. The plugin-level `SHARED_SCRIPTS` grouping goes: those scripts are registered
  rows of the Build plan format entry, so drift covers them, and the import from
  `artifact_models` goes with it.
- **Registry rewrite:** Entries whose rows use shorthand are expanded to one full path per row, and their Canonical
  lines name every canonical file in full: Build plan format (folder rows with "same five
  paths" and multi-path script rows), Architecture template and schema (`.../assets/...`),
  flow.yaml schema (the four sibling schemas and templates added to its Canonical line), Fix
  record format (`find-root-cause/assets/fix-record.template.md` added to its Canonical line),
  Blog bundled files, Business plan format, and Orchestration run log. The Meridian theme
  entry's "Check with `cmp`" sentence says the `copies` check now does it. The Entry shape at
  the bottom gains a whole-file example row.
- **Versions and changelog:** No plugin bump. One `CHANGELOG.md` entry under the PR's date, per
  `decision-changelog-sections.md`.

## Phases

### Phase 1: Registry-driven copies check

- **Builds:** The registry reader, the four failures and the removals in Design, the registry rewrite, and
  the README, `plugins/CLAUDE.md` and changelog updates.
- **Check:** `python tools/validate-plugins/validate.py` exits 0. Then, one at a time, each reverted
  after: (a) append a byte to
  `plugins/standalone/ceh-documentation/skills/write-concept-docs/references/docs-standard.md`:
  exit 1 with a drift error naming it and its canonical file in write-api-reference; (b) in
  `docs/CROSS_REFERENCES.md`, change that row's path to
  `plugins/standalone/ceh-documentation/skills/write-concept-docs-missing/references/docs-standard.md`:
  exit 1 with a stale error for it, plus an unregistered error for the real write-concept-docs
  file; (c) write the same bytes to `references/zz-test.md` in
  `plugins/standalone/ceh-blog/skills/draft-post` and `plugins/standalone/ceh-blog/skills/edit-post`:
  exit 1 with an unregistered error; (d) write different bytes to those two files: exit 0;
  (e) add a second backticked path to the write-concept-docs row: exit 1 with a malformed
  error.
- **Status:** todo

## Open

None

## Record

- 2026-11-07 Planned: status ready
- 2026-11-07 Reviewed: Revise first, 3 blocking (Fix record format missing from the registry rewrite, so its
  template row is malformed on day one; fenced Entry shape example row would be parsed;
  Check (b) renames the file, giving malformed and unregistered, not stale)

<!-- prettier-ignore-end -->
