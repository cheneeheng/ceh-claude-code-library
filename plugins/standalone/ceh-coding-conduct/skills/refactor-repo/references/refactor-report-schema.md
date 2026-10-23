# Refactor report schema

The Phase 4 report `refactor-repo` saves to `.agents_workspace/product/refactor/<YYYY-MM-DD>.md`. A new
report is a copy of `../assets/refactor-report.template.md`, relative to this file. The
`schema: refactor-report/v1` line stays as written.

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
