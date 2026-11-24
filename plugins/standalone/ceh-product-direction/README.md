# ceh-product-direction

Decide what to build and whether it is worth it. The plugin has three entry points:

- `write-vision-and-strategy` writes down a repo's direction so later decisions can be settled
  from it: `VISION.yaml`, why the repo exists and which principles decide, and `STRATEGY.yaml`, how it
  gets there and how work is chosen. The repo can hold code or only documents.
- `write-product-requirements` breaks the product into features: `PRD.yaml`, each feature with
  its user, its requirements, its acceptance criteria and its status, so the next build plan is
  picked from a list.
- `develop-business-plan` turns a product idea, or an existing app plan, into a **validated
  business plan** with a clear product-market fit. It drafts proactively from whatever already
  exists, then runs a disciplined interview loop that attacks the plan's weakest assumption until
  an 8-point PMF readiness gate passes.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Checking and rendering the YAML files
needs [uv](https://docs.astral.sh/uv/). Without it each file is saved unchecked, its Markdown is
not rendered, and the agent is told once per session that the file went unchecked. The business
plan's HTML page needs Node.js 18+ and network access. Without them the Markdown is still written
and the HTML is skipped.

## Skills

| Skill                        | Say or type                                                                                                                                                                                                                                                                                                                                                                                                      | What it does                                                                                                                                                                   |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `write-vision-and-strategy`  | "write the vision doc", "create a strategy doc", `/ceh-product-direction:write-vision-and-strategy`                                                                                                                                                                                                                                                                                                              | Drafts `VISION.yaml` and `STRATEGY.yaml` from what the repo shows, then confirms them with its owner                                                                           |
| `write-product-requirements` | "write the PRD", "break the product into features", `/ceh-product-direction:write-product-requirements`                                                                                                                                                                                                                                                                                                          | Drafts `PRD.yaml`, the product's features with their requirements and acceptance criteria, then confirms it with its owner                                                     |
| `develop-business-plan`      | "write a business plan", "build a business plan from my app plan", "is there product-market fit for this", "validate my product idea", "who would pay for this", "pressure-test my startup idea", "review my business plan", "what's our moat", "do the numbers work", "how do I get my first customers", "run a premortem", "90-day plan", "write a pitch deck", `/ceh-product-direction:develop-business-plan` | The entry point for a business plan: finds the plan, works out the moment, and routes to the specialist that owns it                                                           |
| `find-product-market-fit`    | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | Drafts a business plan proactively, then loops interview and revise until the PMF readiness gate passes                                                                        |
| `review-business-plan`       | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | Report-only board review: scores the plan on seven lenses and names the one finding that most changes it                                                                       |
| `sharpen-strategy`           | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | Where to play, how to win, what to refuse, checked against nine tests of a defensible edge                                                                                     |
| `stress-test-unit-economics` | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | Per-unit model with arithmetic shown, cash low point, and the one input that kills the business                                                                                |
| `plan-go-to-market`          | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | The first ten customers by name, one channel, its arithmetic, and a pass-or-fail channel test                                                                                  |
| `run-premortem`              | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | Assumes the business failed, writes how, and attaches a warning signal, kill criterion, and loss cap                                                                           |
| `set-operating-plan`         | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | A 90-day plan: at most three objectives, owned key results, weekly inputs, a stop-doing list                                                                                   |
| `write-investor-materials`   | Called by `develop-business-plan`                                                                                                                                                                                                                                                                                                                                                                                | A deck outline and outreach notes from a validated plan, every claim citing its plan section. Each slide ends in a `Source: §NN` line and the ask names the milestones it buys |

`write-vision-and-strategy`, `write-product-requirements` and `develop-business-plan` are the
three skills you invoke. The other eight are business plan specialists with no slash command:
`develop-business-plan` calls the right one. After each specialist returns it resets
`status: draft` when the gate has dropped below 8/8, and names the specialist to run next.

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                                                                                                                                     |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact check       | Checks each write to `BUSINESS_PLAN.yaml`, `VISION.yaml`, `STRATEGY.yaml`, `PRD.yaml`, `ARCHITECTURE.yaml`, the business plan review, `INVESTOR_DECK.yaml` and `INVESTOR_OUTREACH.yaml`, and renders its Markdown. Errors go back to the agent to fix, and the Markdown stays as it was. |
| Generated-file guard | Stops a hand edit to a Markdown file that is generated from a YAML file, and names the YAML to edit instead, so the edit is not lost at the next render.                                                                                                                                 |

### What the artifact check reports

An adopted vision, strategy or PRD that still holds `[assumed]` is an error. A `PRD.yaml` is found
by its `schema:` line only, so one that has lost that line is not reported.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the artifact check and the generated-file guard off                  |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### The reader rule

`write-vision-and-strategy` and `write-product-requirements` never read the business plan. The
business plan may read the vision and the strategy. A business plan turns guesses into dated
tests, and a skill that reads it would copy those tests into committed files later sessions treat
as binding.

### How the vision and strategy are written

`write-vision-and-strategy` drafts both docs from what the repo shows, interviews the owner only on
what it cannot show, tests that the docs settle real decisions, and points `CLAUDE.md` at them once
confirmed. The first run writes both files with `status: draft` and `[assumed]` marks before it
asks anything. Only an `adopted` doc gets a pointer from `CLAUDE.md`, so an assumption never binds
a later session. Build skills read these docs and must not read business material, so they carry
no pricing or unit economics.

### How the product requirements are written

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

### How the business plan works

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

### The PMF readiness gate

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

### What it produces

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

### Where the specialist skills come from

Six of the specialist skills turn widely published operating principles into checks an agent can
run. Each test names the leader it is associated with (Drucker, Grove, Buffett, Munger, Bezos,
Walton, Jobs, Dell, Kamprad, Ohno, and others) so the reasoning can be traced. The attributions
are paraphrases of well-known ideas, not quotations, and the skills use them as tests to apply,
never as authority that settles a question.

### With build plans

Validation that surfaces product changes flows into a new `ceh-build-plan` plan, stated as
product changes. The §13 milestones, experiments and kill criteria stay in the business plan. The
flow is one way: no build plan, vision, strategy or decision rule reads the business plan, so its
tests and dates stay in it.

## Not this plugin

- The **technical** build plan, how the app is built: `ceh-build-plan`. It reads the vision and
  the strategy when they exist. This plugin owns the **business** plan (why it sells, who pays),
  reads the build plans as input, and defers product detail to them.
- One feature's plan, not the whole feature list: `ceh-build-plan:write-build-plan`.
- Docs for users of the product: `ceh-documentation`.

## Where its files live

This plugin saves and reads product files in `.agents_workspace/product/`: `VISION.yaml`,
`STRATEGY.yaml` and `PRD.yaml` at its top, or wherever the repo already keeps the vision and
strategy, each with its `.md` rendered beside it. The business plan, its HTML page and the
investor materials go in `.agents_workspace/product/business/`, local and not committed. A
business plan review goes in `.agents_workspace/product/review/business-plan/`. A project with a
root `product/` moves each file to the same sub-path there, or names its location in `CLAUDE.md`.
