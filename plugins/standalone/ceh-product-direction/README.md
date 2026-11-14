# ceh-product-direction

Decide what to build and whether it is worth it. The plugin has two entry points:

- `write-vision-and-strategy` writes down a repo's direction so later decisions can be settled
  from it: `VISION.yaml`, why the repo exists and which principles decide, and `STRATEGY.yaml`, how it
  gets there and how work is chosen. The repo can hold code or only documents.
- `develop-business-plan` turns a product idea — or an existing app plan — into a **validated
  business plan** with a clear product-market fit. It drafts proactively from whatever already
  exists, then runs a disciplined interview loop that attacks the plan's weakest assumption until
  an 8-point PMF readiness gate passes.

## The reader rule

`write-vision-and-strategy` never reads the business plan. The business plan may read the vision
and the strategy. The reason is in `.claude/rules/decision-business-plan-readers.md` in this
library's repo: a business plan turns guesses into dated tests, and a skill that reads it copies
those tests into committed files later sessions treat as binding.

## How the vision and strategy are written

`write-vision-and-strategy` drafts both docs from what the repo shows, interviews the owner only on
what it cannot show, tests that the docs settle real decisions, and points `CLAUDE.md` at them once
confirmed. It writes `.agents_workspace/product/VISION.yaml` and
`.agents_workspace/product/STRATEGY.yaml`, or wherever the repo already keeps the docs, with
`VISION.md` and `STRATEGY.md` rendered beside them. Only an `adopted` doc gets a pointer from
`CLAUDE.md`, so an assumption never binds a later session. Build skills read these docs and must
not read business material, so they carry no pricing or unit economics.

## How the business plan works

`develop-business-plan` is a thin entry point: it finds `BUSINESS_PLAN.yaml`, works out which moment
this is, and calls the specialist skill that owns it. With no plan on disk it first asks whether the
project is a business now or a tool you build for your own use. For your own use it offers to wait,
or to write a `status: dormant` plan, where no specialist writes a test, kill or milestone date
until you say the project is a business. Then it calls `find-product-market-fit`, which is a loop,
not a one-shot generator:

```
Intake   → read build plans (.agents_workspace/product/plans/*.yaml) or any PRD/spec/pitch you provide
Draft v0 → write BUSINESS_PLAN.yaml from what's known; score the PMF gate
Interview→ attack the lowest-scoring gate criterion — one sharp question at a time
Revise   → fold the answer in, re-tag confidence, re-score the gate
         ↺ repeat interview/revise until gate = 8/8 AND you confirm
Validate → flip status to validated; hand off the next experiment
```

If `ceh-build-plan` build plans exist, they seed the draft (their Goal, Scope, and Design
become the product and target-user starting point). If nothing exists, the skill
opens with one grounding question, drafts from your answer, then interrogates.

Every load-bearing claim is tagged `[evidence]`, `[assumption]`, or `[hypothesis-to-test]`. A plan
full of `[assumption]` tags hasn't found product-market fit — it has a to-do list. The loop's job
is to convert each into evidence or a cheap, scheduled test.

## Skills

| Skill                        | Description                                                                                                                                                                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-vision-and-strategy`  | An entry point: draft `VISION.yaml` and `STRATEGY.yaml` from what the repo shows, then confirm them with its owner. It's working if the first run writes both files with `status: draft` and `[assumed]` marks before it asks anything |
| `develop-business-plan`      | The entry point for a business plan: find the plan, work out the moment, and route to the specialist that owns it                                                                                                                      |
| `find-product-market-fit`    | Draft a business plan proactively, then loop interview→revise until the PMF readiness gate passes                                                                                                                                      |
| `review-business-plan`       | Report-only board review: score the plan on seven lenses and name the one finding that most changes it                                                                                                                                 |
| `sharpen-strategy`           | Where to play, how to win, what to refuse, checked against nine tests of a defensible edge                                                                                                                                             |
| `stress-test-unit-economics` | Per-unit model with arithmetic shown, cash low point, and the one input that kills the business                                                                                                                                        |
| `plan-go-to-market`          | The first ten customers by name, one channel, its arithmetic, and a pass-or-fail channel test                                                                                                                                          |
| `run-premortem`              | Assume the business failed, write how, and attach a warning signal, kill criterion, and loss cap                                                                                                                                       |
| `set-operating-plan`         | A 90-day plan: at most three objectives, owned key results, weekly inputs, a stop-doing list                                                                                                                                           |
| `write-investor-materials`   | A deck outline and outreach notes from a validated plan, every claim citing its plan section. It's working if each slide ends in a `Source: §NN` line and the ask names the milestones it buys                                         |

`write-vision-and-strategy` and `develop-business-plan` are the two skills you invoke. The other
eight are business plan specialists and model-only, with no
slash command and a one-line description: they do not trigger on their own, and
`develop-business-plan` calls the right one. After each specialist returns it resets
`status: draft` when the gate has dropped below 8/8, and names the specialist to run next.

Invoke manually:

```
/ceh-product-direction:write-vision-and-strategy
/ceh-product-direction:develop-business-plan
```

**write-vision-and-strategy** loads automatically when you say `"write the vision doc"` or
`"create a strategy doc"`.

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

A single living `BUSINESS_PLAN.yaml` (`business-plan/v3`, 13 sections: problem, target customer,
value prop, solution, competition, market math, business model, go-to-market, traction,
financials, risks, milestones), revised in place across the loop, with a `pmf_gate` score out of 8. Every skill checks it against its model through `uv` before reading it, and `BUSINESS_PLAN.md`
is rendered from it: Mermaid diagrams sit beside the text they show, every heading carries a
nested number (`§12.01.02`), and a linked contents list opens it, all written by the renderer. An
older `BUSINESS_PLAN.md` moves to the YAML on the next run, with a `BUSINESS_PLAN.v2.md` backup.
After every specialist,
`develop-business-plan` rebuilds `BUSINESS_PLAN.html` next to it: one self-contained page in the
Meridian theme with a contents rail and the diagrams rendered. The HTML needs Node.js 18+ and
network access (npx fetches `marked`, the page loads Mermaid from a CDN); without them the
markdown is still written and the HTML is skipped. The schema and
the 8-point gate live in `references/business-plan-schema.md`, copied into each of the nine skills.
`write-investor-materials` writes `INVESTOR_DECK.md` and `INVESTOR_OUTREACH.md` to
`.agents_workspace/product/business/`, local and not committed, and leaves the plan itself unchanged.

## Hooks

After every write to `BUSINESS_PLAN.yaml`, `VISION.yaml` or `STRATEGY.yaml`,
`artifact-render-hook.py` (`PostToolUse`) checks it against its model through `uv` and renders its
Markdown, or reports each error back to the agent and leaves the Markdown as it was. An adopted
vision or strategy that still holds `[assumed]` is one such error. `find-product-market-fit` also carries the architecture
model, to check `.agents_workspace/product/ARCHITECTURE.yaml` before reading it, so the hook acts on a write to that
file too. `generated-md-guard.py` (`PreToolUse`) denies a direct
edit to a generated Markdown file and names its YAML. Both need `uv`: without it the agent is told
once per session that the file went unchecked. `CEH_ARTIFACT_CHECK=off`, or `CEH_DISABLED_HOOKS`
with `artifact-render-hook` or `generated-md-guard`, switches them off.

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

- `ceh-build-plan` owns the **technical** build plan (how the app is built), and reads the vision
  and the strategy when they exist. This plugin owns the **business** plan (why it sells, who
  pays). It reads the build plans as input and
  defers product detail to them rather than duplicating architecture. The flow is one way: no
  build plan, vision, strategy or decision rule reads the business plan, so its tests and dates
  stay in it.
- Validation that surfaces product changes flows into a new `ceh-build-plan` plan, stated as
  product changes. The §13 milestones, experiments and kill criteria stay in the business plan.
- Docs for users of the product: use `ceh-documentation`.
