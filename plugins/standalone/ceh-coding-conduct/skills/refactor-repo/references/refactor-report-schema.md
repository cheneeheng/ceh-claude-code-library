# Refactor report schema

The Phase 4 report `refactor-repo` saves to
`.agents_workspace/product/refactor/<YYYYMMDD-HHMMSS>-<session-id>-refactor.yaml`, with its `.md`
rendered beside it. A reference to it names the `.yaml`. Its layout is
`../assets/refactor-report.template.md`, relative to this file. A new report is written as
`refactor-report/v2` YAML, per the section at the end, and an older `refactor-report/v1` report,
a `.md` with no YAML beside it, stays as written, its `schema:` line included.

## Frontmatter

- `date`: the run date.
- `commit`: the SHA the run started from.

## Sections

One `##` section per cluster, named for the cluster, each with:

- **Applied:** one row per candidate applied, with the `git diff --stat` totals before and after.
- **Skipped:** one row per candidate skipped. Reason is `coverage`, `size`, or `risk`, with a
  short note.
- **Bugs found, not fixed:** each bug found while refactoring, as `path:line` and one line, or
  `none`. They are reported, never fixed, by this run.

## refactor-report/v2: YAML with generated Markdown

A `refactor-report/v2` report is a copy of `../assets/refactor-report.template.yaml`, and the `.md`
of the same name is generated from it in the layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`. The format in code is
`refactor-report-model.py` beside this file, and `scripts/artifact.py` in the skill checks and
renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `clusters.0` is
the first cluster.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `refactor-report/v2`. `date`: an unquoted date. `commit`: 7 to 40 lowercase hex
  characters.
- `clusters`: at least one, in the order the run applied them, each with `name` and three lists:
  `applied` (`candidate`, `before` and `after`, the `git diff --stat` totals), `skipped`
  (`candidate`, `reason`: `coverage`, `size` or `risk`, and `note`), and `bugs` (`location`, a
  `path:line`, and `bug`).
- An empty list is `[]` and renders as `None`, or `none` for `bugs`.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment: `before: '3 files changed, 40 insertions(+), 12 deletions(-)'`.
