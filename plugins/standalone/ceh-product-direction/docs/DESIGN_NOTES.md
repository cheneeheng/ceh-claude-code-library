# ceh-product-direction design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## The reader rule

The reason is in `.claude/rules/decision-business-plan-readers.md` in this
library's repo: a business plan turns guesses into dated tests, and a skill that reads it copies
those tests into committed files later sessions treat as binding.

## Schemas

`write-product-requirements` writes `.agents_workspace/product/PRD.yaml` (`prd/v1`) with `PRD.md`
rendered beside it.

A single living `BUSINESS_PLAN.yaml` (`business-plan/v3`, 13 sections: problem, target customer,
value prop, solution, competition, market math, business model, go-to-market, traction,
financials, risks, milestones), revised in place across the loop, with a `pmf_gate` score out of 8. Every skill checks it against its model through `uv` before reading it, and `BUSINESS_PLAN.md`
is rendered from it: Mermaid diagrams sit beside the text they show, every heading carries a
nested number (`§12.01.02`), and a linked contents list opens it, all written by the renderer. The HTML needs Node.js 18+ and
network access (npx fetches `marked`, the page loads Mermaid from a CDN); without them the
markdown is still written and the HTML is skipped. The schema and
the 8-point gate live in `references/business-plan-schema.md`, copied into each of the nine skills.

## Specialist invocation

The other eight are business plan specialists and model-only, with no
slash command and a one-line description: they do not trigger on their own, and
`develop-business-plan` calls the right one.

## Hook wiring

After every write to `BUSINESS_PLAN.yaml`, `VISION.yaml`, `STRATEGY.yaml` or `PRD.yaml`,
`artifact-render-hook.py` (`PostToolUse`) checks it against its model through `uv` and renders its
Markdown, or reports each error back to the agent and leaves the Markdown as it was. An adopted
vision, strategy or PRD that still holds `[assumed]` is one such error. A `PRD.yaml` is found by
its `schema:` line only, so one that has lost that line is not reported. `find-product-market-fit` also carries the architecture
model, to check `.agents_workspace/product/ARCHITECTURE.yaml` before reading it, so the hook acts on a write to that
file too. It also checks and renders `review-business-plan`'s saved review
(`business-plan-review/v3`, one file whose rounds and lens findings later reviews update in place) and `write-investor-materials`' `INVESTOR_DECK.yaml`
(`investor-deck/v2`) and `INVESTOR_OUTREACH.yaml` (`investor-outreach/v2`). `generated-md-guard.py` (`PreToolUse`) denies a direct
edit to a generated Markdown file and names its YAML. Both need `uv`: without it the agent is told
once per session that the file went unchecked. `CEH_ARTIFACT_CHECK=off`, or `CEH_DISABLED_HOOKS`
with `artifact-render-hook` or `generated-md-guard`, switches them off.

## Location history

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.

## Full trigger list of develop-business-plan

Moved from the README Skills table on 2026-11-24, which keeps three:

"write a business plan", "build a business plan from my app plan", "is there product-market fit for this", "validate my product idea", "who would pay for this", "pressure-test my startup idea", "review my business plan", "what's our moat", "do the numbers work", "how do I get my first customers", "run a premortem", "90-day plan", "write a pitch deck", `/ceh-product-direction:develop-business-plan`

## Investor materials slides

A deck outline and outreach notes from a validated plan, every claim citing its plan section. Each slide ends in a `Source: §NN` line and the ask names the milestones it buys

## How the vision and strategy are written

`write-vision-and-strategy` drafts both docs from what the repo shows, interviews the owner only on
what it cannot show, tests that the docs settle real decisions, and points `CLAUDE.md` at them once
confirmed. The first run writes both files with `status: draft` and `[assumed]` marks before it
asks anything. Only an `adopted` doc gets a pointer from `CLAUDE.md`, so an assumption never binds
a later session. Build skills read these docs and must not read business material, so they carry
no pricing or unit economics.

## How the product requirements are written

`write-product-requirements` drafts the feature list from the vision, the strategy and the repo,
asks the owner one round of questions, and tests that each requirement is observable and each
acceptance item checkable. The first run writes the file with `status: draft` before it asks
anything, and the reply ends with a feature table. The features are in build order, and each has
an id that is never reused, a status (`todo`, `planned` or `built`) and the build plans that
deliver it. What is already built is listed too, so the list is whole. Only an `adopted` file is
free of `[assumed]` marks.

When a later version changes what a built feature does, the new behaviour gets a new id and the
old one becomes a replaced feature: it moves to the file's `replaced` list with its successor,
the reason and the plans that built it. The feature list then always describes the product as
it is now, and the history stays in the same file, marked as history.

## How the business plan works

`develop-business-plan` is a thin entry point: it finds `BUSINESS_PLAN.yaml`, works out which moment
this is, and calls the specialist skill that owns it. With no plan on disk it first asks whether the
project is a business now or a tool you build for your own use. For your own use it offers to wait,
or to write a `status: dormant` plan, where no specialist writes a test, kill or milestone date
until you say the project is a business. Then it calls `find-product-market-fit`, which is a loop,
not a one-shot generator:

```
Intake   → read build plans (.agents_workspace/product/plan/*.yaml) or any PRD/spec/pitch you provide
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
full of `[assumption]` tags has not found product-market fit. It has a to-do list. The loop's job
is to convert each into evidence or a cheap, scheduled test.

## What it produces

A single living `BUSINESS_PLAN.yaml` (13 sections: problem, target customer, value prop, solution,
competition, market math, business model, go-to-market, traction, financials, risks, milestones),
revised in place across the loop, with a `pmf_gate` score out of 8. `BUSINESS_PLAN.md` is rendered
from it: Mermaid diagrams sit beside the text they show, every heading carries a nested number
(`§12.01.02`), and a linked contents list opens it. An older `BUSINESS_PLAN.md` moves to the YAML
on the next run, with a `BUSINESS_PLAN.v2.md` backup. After every specialist,
`develop-business-plan` rebuilds `BUSINESS_PLAN.html` next to it: one self-contained page in the
Meridian theme with a contents rail and the diagrams rendered.

`write-investor-materials` writes `INVESTOR_DECK.yaml` and `INVESTOR_OUTREACH.yaml`, each with its
rendered `.md`, and leaves the plan itself unchanged.

## Where the specialist skills come from

Six of the specialist skills turn widely published operating principles into checks an agent can
run. Each test names the leader it is associated with (Drucker, Grove, Buffett, Munger, Bezos,
Walton, Jobs, Dell, Kamprad, Ohno, and others) so the reasoning can be traced. The attributions
are paraphrases of well-known ideas, not quotations, and the skills use them as tests to apply,
never as authority that settles a question.

## With build plans

Validation that surfaces product changes flows into a new `ceh-build-plan` plan, stated as
product changes. The §13 milestones, experiments and kill criteria stay in the business plan. The
flow is one way: no build plan, vision, strategy or decision rule reads the business plan, so its
tests and dates stay in it.
