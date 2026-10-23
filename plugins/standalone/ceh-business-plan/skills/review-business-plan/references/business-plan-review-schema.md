# Business plan review schema

The report `review-business-plan` saves to `.agents_workspace/product/business-plan-reviews/<YYYY-MM-DD>.md`.
A new report is a copy of `../assets/business-plan-review.template.md`, relative to this file. The
`schema: business-plan-review/v1` line stays as written.

## Frontmatter

- `plan`: the path to the plan reviewed.
- `date`: the review date.
- `verdict`: `build`, `fix first`, or `do not build`.
- `score`: the sum of the lens scores, out of 14.

## Body

- **Verdict:** the frontmatter verdict, then one sentence on why.
- **Score:** the same `<N>/14` as the frontmatter.
- **Headline finding:** the one thing that most changes this plan.
- **Lens table:** one row per lens, seven in all. Score is `0`, `1`, or `2`. Evidence is a quote
  from the plan with its section, or `"nothing found"`. Gap is what is missing, one line.
- **A fresh owner would:** what to stop and what to start with.
- **Strongest part:** the strongest sentence in the plan, quoted, and why it is strong.
- **Run next:** one `<skill> for <lens>` per lens scoring below 2, comma-separated, in order.
