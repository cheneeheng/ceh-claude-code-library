# ceh-business-plan

Claude Code plugin for turning a product idea — or an existing app plan — into a **validated
business plan** with a clear product-market fit. It drafts proactively from whatever already
exists, then runs a disciplined interview loop that attacks the plan's weakest assumption until an
8-point PMF readiness gate passes.

## How it works

The skill is a loop, not a one-shot generator:

```
Intake   → read app plans (SKELETON.md / ITER_NN.md) or any PRD/spec/pitch you provide
Draft v0 → write BUSINESS_PLAN.md from what's known; score the PMF gate
Interview→ attack the lowest-scoring gate criterion — one sharp question at a time
Revise   → fold the answer in, re-tag confidence, re-score the gate
         ↺ repeat interview/revise until gate = 8/8 AND you confirm
Validate → flip status to validated; hand off the next experiment
```

If `plan-build-review` app plans exist, they seed the draft (the §01 Concept, §02 Architecture,
§03 Tech Stack become the product and target-user starting point). If nothing exists, the skill
opens with one grounding question, drafts from your answer, then interrogates.

Every load-bearing claim is tagged `[evidence]`, `[assumption]`, or `[hypothesis-to-test]`. A plan
full of `[assumption]` tags hasn't found product-market fit — it has a to-do list. The loop's job
is to convert each into evidence or a cheap, scheduled test.

## Skills

| Skill                   | Description                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------- |
| `develop-business-plan` | Draft a business plan proactively, then loop interview→revise until the PMF readiness gate passes |

Invoke manually:

```
/ceh-business-plan:develop-business-plan
```

**develop-business-plan** loads automatically when you say:

- `"write a business plan"`
- `"build a business plan from my app plan"`
- `"is there product-market fit for this"`
- `"validate my product idea"`
- `"who would pay for this / find the market for X"`
- `"pressure-test my startup idea"`

## What it produces

A single living `BUSINESS_PLAN.md` (13 sections: problem, target customer, value prop, solution,
competition, market math, business model, go-to-market, traction, financials, risks, milestones),
revised in place across the loop, with a `pmf_gate: N/8` score in its frontmatter. The schema and
the 8-point gate live in `skills/develop-business-plan/references/business-plan-schema.md`.

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

- `ceh-plan-build-review` owns the **technical** build plan (how the app is built). This plugin
  owns the **business** plan (why it sells, who pays). It reads the app plans as input and defers
  product detail to them rather than duplicating architecture.
- Validation that surfaces product changes flows back to `ceh-plan-build-review`; the plan's §13
  milestones become the build/validation backlog.
