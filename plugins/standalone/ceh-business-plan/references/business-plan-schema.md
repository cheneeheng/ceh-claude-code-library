# Business Plan Document Schema

The artifact every skill of this plugin reads and writes. One file, `BUSINESS_PLAN.md`, written to
the repo root (or alongside the app plans it derives from). It is a **living document**: each
interview loop revises it in place, not a fresh copy. When it derives from app plans, it carries a
`derived_from` field naming the plan stems it was built on.

`develop-business-plan` creates the file and owns all 13 sections. The specialist skills each
deepen named sections with one subsection, listed under [Specialist subsections](#specialist-subsections).

## Frontmatter

```yaml
---
artifact: BUSINESS_PLAN
status: draft # draft | validated  (validated = PMF gate passed + user confirmed)
created: YYYY-MM-DD
updated: YYYY-MM-DD
product: <one-line product name>
stage: <idea | prototype | launched | revenue>
derived_from: [] # plan stems this was built on, e.g. [SKELETON, ITER_03]; [] if none
pmf_gate: 0/8 # criteria met out of 8 (see PMF Readiness Gate below)
---
```

`derived_from` names plan artifacts by **stem** (filename without `.md`), matching the
`plan-build-review` convention (`SKELETON`, `ITER_NN`, version-tagged variants like `SKELETON_v2`).

## Sections

Every section carries a **confidence tag** on its riskiest claims: `[evidence]` (backed by a real
data point, quote, or transaction), `[assumption]` (believed but untested — the interview's
hunting ground), or `[hypothesis-to-test]` (an assumption with a named, cheap test attached).
A plan full of `[assumption]` tags has not found product-market fit yet — it has a to-do list.

| ID  | Title                      | Content                                                                                                                                                                                        |
| --- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| §01 | Executive Summary          | Three sentences: what it is, who it's for, why now. Written **last**, regenerated each loop.                                                                                                   |
| §02 | Problem                    | The specific job-to-be-done. Who has it, how often, how painful, what it costs them today. The problem severity is the load-bearing claim — tag it honestly.                                   |
| §03 | Target Customer            | The beachhead segment, not "everyone." Named persona or firmographic. Reachability: where they already are. Why this segment first.                                                            |
| §04 | Value Proposition          | The one-line promise, the before/after, and the single most important differentiator. The "why you, why not the alternative" sentence.                                                         |
| §05 | Solution / Product         | What it does at the level a customer cares about — outcomes, not features. Link to the app plan (`derived_from`) for the technical detail; do not restate architecture here.                   |
| §06 | Alternatives & Competition | What the customer uses today (including spreadsheets, doing nothing, a manual workaround — the real competition is usually inertia). Named competitors, and the wedge that beats each.         |
| §07 | Market                     | TAM / SAM / SOM with the **arithmetic shown** (bottom-up: customers × price, not a top-down analyst number). The SOM 12-month target and the assumption behind it.                             |
| §08 | Business Model & Pricing   | How money is made, who pays, the price point and its basis (value-based, cost-plus, competitor-anchored). Unit economics: rough CAC, LTV, gross margin, payback.                               |
| §09 | Go-to-Market               | The first acquisition channel and why it fits where the customer already is. The motion (self-serve, sales-led, community, content). First 10 customers plan.                                  |
| §10 | Traction & Validation      | Evidence to date: signups, LOIs, pre-orders, interviews, waitlist, prototype usage. Empty is allowed and honest at idea stage — but then §10 names the **next validation experiment** instead. |
| §11 | Financials                 | A lightweight model: revenue drivers, key costs, runway, the break-even or next-raise milestone. Not a 5-year spreadsheet — the three numbers that decide viability.                           |
| §12 | Risks & Unknowns           | The assumptions that, if wrong, kill the business — ranked. Each paired with the cheapest test that would de-risk it. This section feeds the next interview loop.                              |
| §13 | Milestones                 | The next 3–4 dated, falsifiable milestones (each one validates or kills an assumption from §12).                                                                                               |

§05 deliberately defers product detail to the app plan when one exists — the business plan owns
the _why it sells_, the app plan owns the _how it is built_. Do not duplicate architecture, data
models, or API surface here.

## Specialist subsections

Each specialist skill adds one `###` subsection inside an existing section and replaces it in place
on a re-run. The section's original content stays above it. Every claim keeps a confidence tag.

| Section  | Subsection                                                   | Written by                   |
| -------- | ------------------------------------------------------------ | ---------------------------- |
| §04      | Strategy: where we play, how we win, what we refuse          | `sharpen-strategy`           |
| §08, §11 | Unit model, Cash, Sensitivity with the kill input            | `stress-test-unit-economics` |
| §09      | First ten, press release, first taste, channel, channel test | `plan-go-to-market`          |
| §12      | Premortem: failure stories, guards, commitments, cap         | `run-premortem`              |
| §13      | Operating plan: objectives, key results, owners, cadence     | `set-operating-plan`         |

`review-business-plan` reads every section and writes none.

## PMF Readiness Gate

The loop exit condition. The plan is **satisfiable** (`status: validated`) only when all eight
criteria below are met **and** the user explicitly confirms they are satisfied. Each loop, score
the gate honestly in frontmatter (`pmf_gate: N/8`) and report which criteria remain open.

A criterion is "met" when its claim is either backed by `[evidence]` **or** reduced to a named
`[hypothesis-to-test]` with a concrete, cheap, time-boxed experiment — not left as a bare
`[assumption]`. Honest "we will test this next" passes; hand-waving does not.

1. **Problem is real and acute** — §02 names a specific customer who feels this often enough and
   painfully enough to act. Not "would be nice." Severity is evidenced or has a test.
2. **Beachhead is narrow and reachable** — §03 is one nameable segment you can actually reach,
   not "SMBs" or "everyone." You can describe where the first 10 customers physically are.
3. **Differentiation is defensible** — §04/§06 state why the customer picks you over the real
   alternative (including doing nothing), and why that advantage is not trivially copied.
4. **Willingness to pay is established** — §08 ties the price to a value the customer has signaled
   they will pay for (a quote, a comparable spend, a pre-order) — not a guessed number.
5. **Market math is bottom-up and non-trivial** — §07 SOM is built from customers × price with
   stated assumptions, and the result is large enough to matter.
6. **Unit economics can work** — §08 shows a plausible path to LTV > CAC with a sane payback,
   even if the inputs are still estimates.
7. **A credible first channel exists** — §09 names one channel matched to where the customer
   already is, with a first-10-customers plan, not a list of every channel.
8. **The riskiest assumption has a test** — §12 ranks the kill-risks and pairs the top one with
   the cheapest experiment that would settle it, scheduled in §13.

When fewer than 8 are met, the open criteria **are the agenda** for the next interview loop —
attack the lowest-scoring, highest-leverage one first.
