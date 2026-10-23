# Period retro schema

The retro `review-recent-work` saves: `product/retros/<YYYY-MM-DD>-period.md` for the retro and its
in-scope issues, `.agents_workspace/product/retros/<YYYY-MM-DD>-period.md` for out-of-scope issues. A new
file is a copy of `../assets/period-retro.template.md`, relative to this file. The
`schema: period-retro/v1` line stays as written.

## Frontmatter

- `since`, `until`: the first and last day of the period.
- `other_file`: the path of the matching file in the other folder, or `none`. When both files
  exist, each links the other.

## Sections

- **Shipped:** one bullet per change, as `<type(scope)>: <one line>`, then its PR numbers.
- **Flow:** the three measures, each with where the value came from: PRs merged (`gh pr list` or
  the merges), median time to merge (PR `createdAt` to `mergedAt`), and reverts
  (`git log --grep='^Revert'`). Then the churn hotspots: each path with its commit count,
  separated by commas.
- **Issues:** one numbered `### <n>. <Kind>: <what went wrong>` per issue. **Evidence** names the
  commits or PRs. **Route** names the skill, or `user: <where the fix lands>`. **Status** is
  `handed off: <plan, fix record, or commit>` or `open: <why>`.
- **Questions the history cannot answer:** one bullet per question.
