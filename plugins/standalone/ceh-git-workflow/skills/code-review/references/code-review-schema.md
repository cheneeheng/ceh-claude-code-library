# Code review schema

The review `code-review` saves to `.agents_workspace/product/code-reviews/<branch>-<YYYY-MM-DD>.md` when
its comments are not posted on a PR. A new review is a copy of
`../assets/code-review.template.md`, relative to this file. The `schema: code-review/v1` line
stays as written.

## Frontmatter

- `branch`: the branch reviewed.
- `date`: the review date.
- `verdict`: `Approve`, `Request changes`, `Comment`, or `Cannot verify`, per the verdict table in
  the skill.

## Body

- **Verdict:** the same verdict, then what must change to flip it to approve, or what settles it.
- **Summary:** one or two sentences: what the change does and the overall read.
- **Line comments:** one bullet per comment: the `path:line`, the label `[blocking]`,
  `[advisory]`, or `[question]`, then the comment.
