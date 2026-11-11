---
date: 2026-11-11
session: 39c94071
subject: A business plan's gates leaked into a project's vision, strategy and build plans
files: plugins/standalone/ceh-vision-and-strategy, ceh-build-planning, ceh-business-plan, ceh-every-session, ceh-blog, ceh-seo
---

# Retro: the business plan's gates leaked into the vision, the strategy and the build plans

Date: 2026-11-11. Session: 39c94071. Report only. No skill, plugin or project document was
changed. The fixes belong in the plugin repo (`ceh-claude-code-library`) and are the author's to
make.

Written in `ceh-nightshift` and moved here on 2026-11-11, where the changes land. Figures quoted
from Nightshift's private business plan were removed in the move, per "never quote private
workspace docs in public material".

## What went wrong

Nightshift was meant to be a system the author can use, shared later if it works. Six days in,
its committed documents define success in a business plan's terms: a ten-task test that gates
releases and settings, a build-hour count, and stages for outside users. The author's words on
2026-11-11: the project "is really tied up to all the gates and dates related to a business
plan".

## What I checked

- **Checked:** `git log -S` for each gate term across `product/`, the workspace's git log for
  the business plan, grep counts across `product/`, `nightshift/`, `plugin/` and `tests/`, and
  the skill files in the local plugin cache named below.
- **Read in full:** `product/VISION.md`, `product/STRATEGY.md`, proposal page 08, the review of
  2026-11-11.
- **Not read:** the business plan's body beyond its headings and grep hits, the slice plans'
  bodies, the session transcripts of 2026-11-05 and 2026-11-06.
- **Not known:** which plugin versions were installed on 2026-11-05 and 2026-11-06. The quotes
  are from the newest cached versions. The same lines exist in the oldest cached versions of
  `ceh-vision-and-strategy` (1.0.0) and `ceh-build-planning` (1.1.3, at the old path).

## How it happened, in order

- **2026-11-05, during the day:** the proposal lands in `product/proposal/`. No gate term is in
  `product/` yet.
- **2026-11-05 23:24:** the business plan is committed to the workspace with
  `status: validated`. Its interview rounds invent the ten-task test and its pass mark, a
  build-hour budget, an hours-saved-per-job figure, and stage 2.
- **2026-11-05 23:45:** the premortem adds kill criteria with dates and the SOUL.md replay test.
- **2026-11-06 11:04:** `VISION.md` and `STRATEGY.md` are adopted (`53fa90c`). This commit is the
  first in `product/` to hold "ten-task", "ten real tasks" and "build hours".
- **2026-11-06 11:57:** the five slice plans land (`f6baa1a`), each with
  `business_plan: .agents_workspace/product/business/BUSINESS_PLAN.md` in its frontmatter and
  "The product is in the business plan's §05" in its goal.
- **2026-11-10 and 2026-11-11:** design decisions hang on the test. Merge stays `you` "until the
  ten-task test passes", and a second agent waits for it (`39e3e08`, `13ad5c7`).
- **2026-11-10 and 2026-11-11:** two reviews read the business plan and the proposal as one
  subject. The second adds more gates: a second gate before Merge `auto`, and a 20-minute saving
  that ends the work loop's build.

## Where the gates sit today

| Place                              | What it holds                                                                                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `product/VISION.md`                | The vision paragraph ("Once ten real tasks show work you accept"), goal 1 (the pass mark), the first non-goal (outside users before goal 1) |
| `product/STRATEGY.md`              | "private until ten real tasks pass", the ten-task count and build hours as measures, the second-agent rule                                  |
| `product/plans/first-job-*.md`     | The `business_plan` key and the §05 pointer in all six. Slice 5 also cites the premortem and the ten-task test                              |
| `product/proposal/`                | Pages 03 and 08 and the config template, on Merge and the second agent                                                                      |
| `nightshift/`, `plugin/`, `tests/` | Nothing                                                                                                                                     |

## Causes

### 1. The skills read the business plan by design

- `write-vision-and-strategy` step 2 lists
  `.agents_workspace/product/business/BUSINESS_PLAN.md` among what to read "when present".
- `write-build-plan` step 1: "When `.agents_workspace/product/business/BUSINESS_PLAN.md` exists,
  set `business_plan` and take the goal and target user from it rather than restating them."
- `review-build-plan` reads it when `business_plan` is set. `whats-next`,
  `record-project-decisions`, `ceh-blog:draft-post` and `ceh-seo:write-project-listing-text`
  name it too.
- The author's own rule in `SOUL.md` places business material in the workspace because "no stage
  reads them". The plugins contradict that rule: three stages read it.

### 2. The vision skill's guard names the wrong things

- Its rule: neither doc "carries pricing, unit economics, kill criteria, contacts, or a home
  path".
- What crossed was none of those. It was a validation experiment (§10), a customer stage (§03)
  and a cost measure (§08).
- The skill's "Checkable goal" test asks for a goal someone can tell is met. In a repo with no
  code, the only ready numbers were the business plan's, so its experiment became goal 1. This
  step is my inference: the drafting session's transcript was not read.

### 3. A committed plan points into the private workspace

- The plan schema makes `business_plan` a frontmatter key and replaces the goal with "one
  sentence plus a pointer to its product section".
- So a committed, readable plan sends its reader to a private file to learn what the product
  is. The vision skill forbids quoting `.agents_workspace/`, and the build-plan skill requires
  linking to it.

### 4. The business plan suite has no mode for a project that is not a business yet

- `find-product-market-fit` converts every bare assumption into a scheduled experiment, and
  `run-premortem` requires "a number and a date" per risk and refuses to weaken one later.
- Both are right for a venture. For a tool the author builds for their own use, they produce
  gates and deadlines for a customer question nobody is asking yet.
- Nothing in `develop-business-plan` asks whether the project wants that now.

### 5. Order

- The plan was written and marked `validated` before any job ran end to end, so every number in
  it is a guess. Then every later skill treated a validated plan as a source.
- No skill warns that a business plan written before the product works will shape the vision.

## What to keep

- The plan itself, and the premortem's habit of dated kill criteria, for the day the author
  decides to share Nightshift.
- The protections that came up in the same reviews and guard the author, not a business: the
  Private-text check, hard limits in scripts and permissions, the merge as the yes, the weekly
  usage gate.
- The page 08 tests and the SOUL.md replay as things to learn, without a deadline.

## Proposed skill changes

These are my proposals, not decisions. None is applied.

1. **`ceh-vision-and-strategy:write-vision-and-strategy`:** stop reading the business plan, or
   read it only for who the product is for. Widen the guard from "pricing, unit economics, kill
   criteria" to every gate, date, stage and validation experiment from a business plan. A goal's
   measure comes from the owner in the interview.
2. **`ceh-build-planning:write-build-plan` and the plan schema:** drop the `business_plan` key
   and the §05 pointer. A plan states its own goal, taken from the vision or the request.
3. **`ceh-build-planning:review-build-plan`:** review against the code, the vision and the
   strategy only.
4. **`ceh-business-plan:develop-business-plan`:** ask first whether the project is a business
   now or a tool for the author's own use. For the second, offer to wait, or write the plan as
   dormant with no dates.
5. **`ceh-business-plan:run-premortem` and `find-product-market-fit`:** keep kill criteria and
   experiments inside the plan. Neither writes a to-do or a gate that a build stage reads.
6. **One rule for all of them, in the library's own vision or rules:** information flows from
   the vision to the business plan, never back. This matches "no stage reads them" and gives one
   mechanism in place of a per-skill list.
7. **A check, if a miss repeats:** a grep in the vision and build-plan validators that fails on
   `.agents_workspace/` or `BUSINESS_PLAN` in a committed document. Not proposed as a hook now,
   since this is the first measured miss.

## Open for the author

- Whether the business plan suite should also read nothing from `product/plans/`
  (`find-product-market-fit` Phase 0 reads the build plans). That direction did no harm here.
- Whether `whats-next`, `draft-post` and `write-project-listing-text` may keep reading the plan.
  They suggest or write public text, and a gate could surface there the same way.
- What happens to Nightshift's own documents: stripping the gates from the vision, the strategy,
  the proposal and the slice plans is a separate change in this repo, not started.

## Decided

- 2026-11-11: the author chose to cut the business plan from every skill that writes a committed
  product document: `write-vision-and-strategy`, `write-build-plan`, `review-build-plan` and
  `record-project-decisions`. `draft-post`, `write-project-listing-text` and `whats-next` keep
  reading it. This settles proposals 1 to 3 and 6 and the second open question, in
  `product/plans/business-plan-one-way.yaml` and `.claude/rules/decision-business-plan-readers.md`.
- Proposals 4, 5 and 7 and the first open question stay open.
