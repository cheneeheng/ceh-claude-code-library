# Business plan review schema

The report `review-business-plan` saves to
`.agents_workspace/product/review/business-plan/<YYYYMMDD-HHMMSS>-<session-id>-business-plan-review.yaml`,
with its `.md` rendered beside it. A reference to it names the `.yaml`. Its layout is
`../assets/business-plan-review.template.md`, relative to this file. A new report is written as
`business-plan-review/v2` YAML, per the section at the end, and an older
`business-plan-review/v1` report, a `.md` with no YAML beside it, stays as written, its `schema:`
line included.

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

## business-plan-review/v2: YAML with generated Markdown

A `business-plan-review/v2` report is a copy of `../assets/business-plan-review.template.yaml`,
and the `.md` of the same name is generated from it in the layout above, beside it. The YAML is
the source: agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`. The format in code is
`business-plan-review-model.py` beside this file, and `scripts/artifact.py` in the skill checks
and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `lenses.0` is
Customer.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `business-plan-review/v2`. `plan`, `verdict`: as in `v1`. `product`: the product
  named in the heading. `date`: an unquoted date.
- `verdict_reason`: the sentence after the verdict. `score`: the total, an integer from 0 to 14,
  rendered as `N/14`, and equal to the sum of the lens scores. The verdict is checked against the
  scores: `build` is exactly no lens at 0 and a total of 10 or more, and `do not build` needs
  Customer at 0.
- `headline_finding`: the headline finding.
- `lenses`: `lens`, `score` (0 to 2), `evidence` and `gap`, the seven lenses in the skill's order:
  Customer, Edge, Focus, Money, Reach, Survival, Execution.
- `fresh_owner`: `stop` and `start`. `strongest_part`: `quote`, with its quote marks, and `why`.
- `run_next`: `skill` and `lens`, one per lens below 2, in lens order, and `[]` when none is,
  which renders as `none`.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment: `evidence: '"We charge per seat" (§08)'`.
