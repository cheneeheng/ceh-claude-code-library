# Business plan review schema

The report `review-business-plan` saves to
`.agents_workspace/product/review/business-plan/<YYYYMMDD-HHMMSS>-business-plan-review.yaml`, with
its `.md` rendered beside it, one file edited in place by every later review of the business plan.
A reference to it names the `.yaml`. Its layout is `../assets/business-plan-review.template.md`,
relative to this file. A new report is written as `business-plan-review/v3` YAML, per the section
at the end. An older `business-plan-review/v2` file is converted in place when a new round finds
it, per the Review lifecycle, and a `business-plan-review/v1` report, a `.md` with no YAML beside
it, stays as written.

## Review lifecycle

Every saved review follows these rules, whatever its kind. The section is copied word for word
into each review format's schema, and only the Targets line differs.

- **Name:** `.agents_workspace/product/review/<kind>/<YYYYMMDD-HHMMSS>-<target>.yaml`, the time
  from one `date +%Y%m%d-%H%M%S` call when the file is first saved, never changed after. It
  carries no session id, because several sessions edit a review in place.
- **Lookup:** match names in the kind's folder against
  `^\d{8}-\d{6}-([0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}-)?<target>\.yaml$`, so an older name
  with a session id counts and `layout` never matches `workspace-layout`, and take the newest by
  time prefix. With none, save a new file. Older duplicates are left as written.
- **Convert:** a found file of the kind's older YAML version is rewritten in place to the new one,
  its content becoming round 1 and each of its findings `open`, keeping its name.
- **Cold round:** the reviewer reads the target before the review file, and a subagent reviewer
  gets the target and never the file, so earlier rounds cannot anchor it.
- **Re-check:** before a round is merged, each `open` finding is read against the current target
  and set `fixed`, with the resolution `found fixed in round <n>`, where the target no longer has
  the defect.
- **Merge:** a finding that repeats an `open` one is not added again, and one that repeats a
  `fixed` one reopens it with a note in its resolution.
- **Tick off:** the session that makes a fix sets the finding's status and resolution (the edit,
  commit or PR, or why it will not be fixed) when it knows of the review file.
- **Targets:** a business plan review's target is the fixed name `business-plan-review`.

## Body

- **Verdict:** the latest round's verdict, with the round number, then one sentence on why.
- **Score:** the latest round's score, `<N>/14`.
- **Headline finding:** the one thing that most changes this plan, in the latest round.
- **Lens table:** the latest round, one row per lens, seven in all. Score is `0`, `1`, or `2`.
  Evidence is a quote from the plan with its section, or `"nothing found"`. Gap is what is
  missing, one line.
- **A fresh owner would:** what to stop and what to start with.
- **Strongest part:** the strongest sentence in the plan, quoted, and why it is strong.
- **Run next:** one `<skill> for <lens>` per lens scoring below 2, comma-separated, in order.
- **Findings:** one bullet per lens gap across every round, with the round that raised it and its
  status, `open`, `fixed: <resolution>` or `won't fix: <resolution>`.
- **Earlier rounds:** one line per round before the latest: its date, verdict, score and
  headline finding. Left out with one round.

## business-plan-review/v3: YAML with generated Markdown

A `business-plan-review/v3` report is a copy of `../assets/business-plan-review.template.yaml`,
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
failure, and `3` means no model for that version, as for a `v2` file before it is converted.
Field paths count from 0, so `rounds.0.lenses.0` is round 1's Customer.

**Keys**, each required unless marked optional, and no other key allowed, every value one line:

- `schema`: `business-plan-review/v3`. `plan`: the path to the plan reviewed. `product`: the
  product named in the heading.
- `rounds`: at least one, oldest first, each with:
  - `date`: an unquoted date. `verdict`: `build`, `fix first` or `do not build`.
    `verdict_reason`: the sentence after the verdict.
  - `score`: the total, an integer from 0 to 14, rendered as `N/14`, and equal to the sum of the
    lens scores. The verdict is checked against the scores: `build` is exactly no lens at 0 and a
    total of 10 or more, and `do not build` needs Customer at 0.
  - `headline_finding`: the headline finding.
  - `lenses`: `lens`, `score` (0 to 2), `evidence` and `gap`, the seven lenses in the skill's
    order: Customer, Edge, Focus, Money, Reach, Survival, Execution.
  - `fresh_owner`: `stop` and `start`. `strongest_part`: `quote`, with its quote marks, and `why`.
  - `run_next`: `skill` and `lens`, one per lens below 2, in lens order, and `[]` when none is,
    which renders as `none`.
- `findings`: each with `round` (the 1-based round that raised it), `lens` (one that scored below
  2 in that round), `gap`, `status` (`open`, `fixed` or `won't fix`), and `resolution`
  (optional), required exactly when `status` is not `open`. Every lens below 2 in the latest round
  has an `open` finding, so a gap the plan still has is never ticked off.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment: `evidence: '"We charge per seat" (§08)'`.
