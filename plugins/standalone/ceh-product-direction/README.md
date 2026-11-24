# ceh-product-direction

Decide what to build and whether it is worth it. The plugin has three entry points:

- `write-vision-and-strategy` writes down a repo's direction so later decisions can be settled
  from it: `VISION.yaml`, why the repo exists and which principles decide, and `STRATEGY.yaml`, how
  it gets there and how work is chosen. The repo can hold code or only documents.
- `write-product-requirements` breaks the product into features: `PRD.yaml`, each feature with
  its user, its requirements, its acceptance criteria and its status, so the next build plan is
  picked from a list.
- `develop-business-plan` turns a product idea, or an existing app plan, into a validated business
  plan with a clear product-market fit (PMF). It drafts from what already exists, then questions
  the plan's weakest assumption until an 8-point readiness gate passes.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Checking and rendering the YAML files
needs [uv](https://docs.astral.sh/uv/). Without it each file is saved unchecked, its Markdown is
not rendered, and the agent is told once per session that the file went unchecked. The business
plan's HTML page needs Node.js 18+ and network access. Without them the Markdown is still written
and the HTML is skipped.

## Skills

| Skill                        | Say or type                                                                                                            | What it does                                                                                              |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `write-vision-and-strategy`  | "write the vision doc", "create a strategy doc", `/ceh-product-direction:write-vision-and-strategy`                    | Drafts `VISION.yaml` and `STRATEGY.yaml` from what the repo shows, then confirms them with its owner      |
| `write-product-requirements` | "write the PRD", "break the product into features", `/ceh-product-direction:write-product-requirements`                | Drafts `PRD.yaml`, the product's features with requirements and acceptance criteria, then confirms it     |
| `develop-business-plan`      | "write a business plan", "validate my product idea", "run a premortem", `/ceh-product-direction:develop-business-plan` | The entry point for a business plan: finds the plan, works out the moment, and calls the right specialist |
| `find-product-market-fit`    | Called by `develop-business-plan`                                                                                      | Drafts the plan, then asks and revises until the PMF readiness gate passes                                |
| `review-business-plan`       | Called by `develop-business-plan`                                                                                      | Report-only board review: scores seven lenses and names the one finding that most changes the plan        |
| `sharpen-strategy`           | Called by `develop-business-plan`                                                                                      | Where to play, how to win, what to refuse, checked against nine tests                                     |
| `stress-test-unit-economics` | Called by `develop-business-plan`                                                                                      | Per-unit model with the arithmetic shown, the cash low point, and the one input that kills the business   |
| `plan-go-to-market`          | Called by `develop-business-plan`                                                                                      | The first ten customers, one channel, its arithmetic, and a pass-or-fail channel test                     |
| `run-premortem`              | Called by `develop-business-plan`                                                                                      | Writes how the business failed, with a warning signal, kill criterion and loss cap per top risk           |
| `set-operating-plan`         | Called by `develop-business-plan`                                                                                      | A 90-day plan: at most three objectives, owned key results, weekly inputs, a stop-doing list              |
| `write-investor-materials`   | Called by `develop-business-plan`                                                                                      | A deck outline and outreach notes from a validated plan, every claim citing its plan section              |

You invoke the first three. The other eight have no slash command: `develop-business-plan` calls
the right one and then names the one to run next. When the gate drops below 8/8, it sets the plan
back to `status: draft`.

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                                                                                                                                                                                               |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact check       | Checks each write to `BUSINESS_PLAN.yaml`, `VISION.yaml`, `STRATEGY.yaml`, `PRD.yaml`, `ARCHITECTURE.yaml`, the business plan review, `INVESTOR_DECK.yaml` and `INVESTOR_OUTREACH.yaml`, and renders its Markdown. Errors go back to the agent to fix, and the Markdown stays as it was. An adopted file that still holds `[assumed]` is an error. |
| Generated-file guard | Stops a hand edit to a Markdown file that is generated from a YAML file, and names the YAML to edit instead, so the edit is not lost at the next render.                                                                                                                                                                                           |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the artifact check and the generated-file guard off                  |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### Vision, strategy and requirements

Both skills draft from the repo and save the file with `status: draft` and `[assumed]` marks
before they ask anything. They then ask the owner only what the repo cannot show. Only an
`adopted` doc gets a pointer from `CLAUDE.md`, so an assumption never binds a later session.

`PRD.yaml` lists the features in build order, including what is already built. Each has an id
that is never reused, a status (`todo`, `planned` or `built`) and the build plans that deliver it.
When a built feature's behaviour changes, the new behaviour gets a new id and the old one moves to
the file's `replaced` list.

### The business plan

With no plan on disk, `develop-business-plan` first asks whether the project is a business now or
a tool you build for your own use. For your own use it offers to wait, or to write a
`status: dormant` plan that gets no test, kill or milestone dates until you say it is a business.

Otherwise `find-product-market-fit` drafts `BUSINESS_PLAN.yaml` from your build plans or any spec
you give it. With nothing to read, it asks one grounding question first. It then asks one question
at a time about the weakest gate criterion and revises the plan, until all eight hold and you
confirm. Every key claim is tagged `[evidence]`, `[assumption]` or `[hypothesis-to-test]`.

The gate passes when each of these is evidenced or has a named cheap test:

1. Problem is real and acute
2. Beachhead is narrow and reachable
3. Differentiation is defensible
4. Willingness to pay is established
5. Market math is bottom-up and non-trivial
6. Unit economics can work
7. A credible first channel exists
8. The riskiest assumption has a test

The plan has 13 sections and a `pmf_gate` score out of 8. `BUSINESS_PLAN.md` is rendered from it,
and `BUSINESS_PLAN.html`, one self-contained page, is rebuilt after every specialist. An older
`BUSINESS_PLAN.md` moves to the YAML on the next run, with a `BUSINESS_PLAN.v2.md` backup.
`write-investor-materials` writes `INVESTOR_DECK.yaml` and `INVESTOR_OUTREACH.yaml` and leaves the
plan unchanged.

### The reader rule

The business plan may read the vision, the strategy and the build plans. No vision, strategy,
requirements, build plan or decision rule reads the business plan, so its guesses, tests and dates
stay in it. Product changes found while validating go into a new `ceh-build-plan` plan.

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
root `product/` folder moves each file to the same sub-path under `.agents_workspace/product/`, or
names its own location in `CLAUDE.md`.
