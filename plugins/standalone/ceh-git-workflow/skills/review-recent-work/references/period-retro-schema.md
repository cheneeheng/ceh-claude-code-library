# Period retro schema

The retro `review-recent-work` saves:
`.agents_workspace/product/retros/<YYYYMMDD-HHMMSS>-<session-id>-period.md`, unless the repo's
`CLAUDE.md` names another location. One file holds the retro and every issue, whether its fix
lands in this repo or outside it, because the two files of `v1` would share one name in one folder.
A new file is a copy of `../assets/period-retro.template.md`, relative to this file. The
`schema: period-retro/v2` line stays as written.

A `period-retro/v1` file, an in-repo file and a local file that link each other through
`other_file`, is still read: its issues are the issues of both files.

## Frontmatter

- `since`, `until`: the first and last day of the period.

## Sections

- **Shipped:** one bullet per change, as `<type(scope)>: <one line>`, then its PR numbers.
- **Flow:** the three measures, each with where the value came from: PRs merged (`gh pr list` or
  the merges), median time to merge (PR `createdAt` to `mergedAt`), and reverts
  (`git log --grep='^Revert'`). Then the churn hotspots: each path with its commit count,
  separated by commas.
- **Issues:** one numbered `### <n>. <Kind>: <what went wrong>` per issue. **Evidence** names the
  commits or PRs. **Route** names the skill, or `user: <where the fix lands>` for a fix outside
  this repo. **Status** is `handed off: <plan, fix record, or commit>` or `open: <why>`.
- **Questions the history cannot answer:** one bullet per question.
