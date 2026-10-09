# ceh-business-plan

Claude Code plugin for turning a product idea — or an existing app plan — into a **validated
business plan** with a clear product-market fit. It drafts proactively from whatever already
exists, then runs a disciplined interview loop that attacks the plan's weakest assumption until an
8-point PMF readiness gate passes.

## How it works

`develop-business-plan` is a thin entry point: it finds `BUSINESS_PLAN.md`, works out which moment
this is, and calls the specialist skill that owns it. With no plan on disk it always calls
`find-product-market-fit`, which is a loop, not a one-shot generator:

```
Intake   → read build plans (docs/plans/*.md) or any PRD/spec/pitch you provide
Draft v0 → write BUSINESS_PLAN.md from what's known; score the PMF gate
Interview→ attack the lowest-scoring gate criterion — one sharp question at a time
Revise   → fold the answer in, re-tag confidence, re-score the gate
         ↺ repeat interview/revise until gate = 8/8 AND you confirm
Validate → flip status to validated; hand off the next experiment
```

If `ceh-build-planning` build plans exist, they seed the draft (their Goal, Scope, and Design
become the product and target-user starting point). If nothing exists, the skill
opens with one grounding question, drafts from your answer, then interrogates.

Every load-bearing claim is tagged `[evidence]`, `[assumption]`, or `[hypothesis-to-test]`. A plan
full of `[assumption]` tags hasn't found product-market fit — it has a to-do list. The loop's job
is to convert each into evidence or a cheap, scheduled test.

## Skills

| Skill                        | Description                                                                                                                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `develop-business-plan`      | The entry point: find the plan, work out the moment, and route to the specialist that owns it                                                                                                  |
| `find-product-market-fit`    | Draft a business plan proactively, then loop interview→revise until the PMF readiness gate passes                                                                                              |
| `review-business-plan`       | Report-only board review: score the plan on seven lenses and name the one finding that most changes it                                                                                         |
| `sharpen-strategy`           | Where to play, how to win, what to refuse, checked against nine tests of a defensible edge                                                                                                     |
| `stress-test-unit-economics` | Per-unit model with arithmetic shown, cash low point, and the one input that kills the business                                                                                                |
| `plan-go-to-market`          | The first ten customers by name, one channel, its arithmetic, and a pass-or-fail channel test                                                                                                  |
| `run-premortem`              | Assume the business failed, write how, and attach a warning signal, kill criterion, and loss cap                                                                                               |
| `set-operating-plan`         | A 90-day plan: at most three objectives, owned key results, weekly inputs, a stop-doing list                                                                                                   |
| `write-investor-materials`   | A deck outline and outreach notes from a validated plan, every claim citing its plan section. It's working if each slide ends in a `Source: §NN` line and the ask names the milestones it buys |

`develop-business-plan` is the only skill you invoke. The other eight are model-only, with no
slash command and a one-line description: they do not trigger on their own, and
`develop-business-plan` calls the right one. After each specialist returns it resets
`status: draft` when the gate has dropped below 8/8, and names the specialist to run next.

Invoke manually:

```
/ceh-business-plan:develop-business-plan
```

## Where the specialist skills come from

Six of the specialist skills turn widely published operating principles into checks an agent can
run. Each test names the leader it is associated with (Drucker, Grove, Buffett, Munger, Bezos,
Walton, Jobs, Dell, Kamprad, Ohno, and others) so the reasoning can be traced. The attributions
are paraphrases of well-known ideas, not quotations, and the skills use them as tests to apply,
never as authority that settles a question.

**develop-business-plan** loads automatically when you say:

- `"write a business plan"`
- `"build a business plan from my app plan"`
- `"is there product-market fit for this"`
- `"validate my product idea"`
- `"who would pay for this / find the market for X"`
- `"pressure-test my startup idea"`
- `"review my business plan"`, `"what's our moat"`, `"do the numbers work"`
- `"how do I get my first customers"`, `"run a premortem"`, `"90-day plan"`
- `"write a pitch deck"`

## What it produces

A single living `BUSINESS_PLAN.md` (13 sections: problem, target customer, value prop, solution,
competition, market math, business model, go-to-market, traction, financials, risks, milestones),
revised in place across the loop, with a `pmf_gate: N/8` score in its frontmatter. The schema and
the 8-point gate live in `references/business-plan-schema.md`, shared by all nine skills.
`write-investor-materials` writes `INVESTOR_DECK.md` and `INVESTOR_OUTREACH.md` beside the plan
and leaves the plan itself unchanged.

## The PMF readiness gate

The plan is "satisfiable" only when all eight hold (each evidenced or reduced to a named cheap
test) and you confirm:

1. Problem is real and acute
2. Beachhead is narrow and reachable
3. Differentiation is defensible
4. Willingness to pay is established
5. Market math is bottom-up and non-trivial
6. Unit economics can work
7. A credible first channel exists
8. The riskiest assumption has a test

## Relationship to other plugins

- `ceh-build-planning` owns the **technical** build plan (how the app is built). This plugin
  owns the **business** plan (why it sells, who pays). It reads the build plans as input and
  defers product detail to them rather than duplicating architecture. A build plan in turn points
  to `BUSINESS_PLAN.md` for the goal and target user instead of restating them.
- Validation that surfaces product changes flows into a new `ceh-build-planning` plan; the plan's
  §13 milestones become the build/validation backlog.
