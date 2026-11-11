---
schema: plan/v2
generated_from: business-plan-one-way.yaml
generated_note: "Do not edit. artifact.py renders this file from business-plan-one-way.yaml: edit the YAML, then run artifact.py render."
title: The business plan feeds no committed product document
status: ready
created: 2026-11-11
---

<!-- prettier-ignore-start -->

## Goal

The fixes from `product/retros/2026-11-11-39c94071-business-plan-leak.md`, on the reader split the
user chose on 2026-11-11: the skills that write committed product documents stop reading the
business plan, so its tests, stages, dates and experiments cannot become a project's vision
goals, plan goals or decision rules. Those are `ceh-vision-and-strategy:write-vision-and-strategy`,
`ceh-build-planning:write-build-plan`, `ceh-build-planning:review-build-plan` and
`ceh-every-session:record-project-decisions`. The Tell skills (`ceh-blog:draft-post`,
`ceh-seo:write-project-listing-text`) keep reading it for audience and positioning, and
`ceh-every-session:whats-next` keeps checking that it exists. The flow that matters: in a repo
holding `.agents_workspace/product/business/BUSINESS_PLAN.md`, a vision drafted and a build plan
written take their goals from the owner, the request and the vision, and neither links to the
business plan.

## Scope

**In:**

- One rule, the business plan flows one way: the vision, the strategy and the build plans may
  feed it, and no skill that writes a committed product document reads it. A new
  `.claude/rules/decision-business-plan-one-way.md`, written through
  `ceh-every-session:record-project-decisions`, and `decision-artifact-locations.md` changed
  from "even though Build and Tell read the plan" to "even though Tell reads the plan".
- `docs/STRATEGY.md` says the same: the Build-planning paragraph (line 46), the spine table's
  Build row (line 54), the Shape-to-Build paragraph (lines 58 to 63), and the business-material
  bullet (lines 103 to 106).
- `write-vision-and-strategy` reads no business plan in step 2, its Rules guard names every
  gate, date, stage and validation experiment a business plan holds besides pricing, unit
  economics, kill criteria and contacts, and its Checkable goal test takes a goal's measure
  from the owner or the repo, never a business plan.
- `record-project-decisions` lists no business plan among the decisions already written down,
  and reads no business plan section body.
- `write-build-plan` sets no `business_plan` key and takes the goal and target user from the
  request, the vision and the strategy. `review-build-plan` reviews against the code, the vision
  and the strategy only.
- The plan format: `plan-schema.md` marks `business_plan` as a legacy key that no skill sets or
  follows, and drops the Goal's "pointer to its product section". `plan.template.yaml` and
  `plan.template.md` drop the key. `plan-model.py` still accepts it, so a `plan/v2` plan that
  holds it still validates. All six copies change together.
- Orphans removed: the four business-plan format files (`business-plan-schema.md`,
  `business-plan-model.py`, `business-plan.template.md`, `business-plan.template.yaml`) in the
  four skills that stop reading the plan, their 16 rows in the `docs/CROSS_REFERENCES.md`
  "Business plan format" entry, whose Shared text becomes the sentence in Design "Registry
  text", and `BUSINESS_PLAN` in the `compatibility` lines of `write-build-plan`,
  `review-build-plan` and `record-project-decisions` (the vision skill's line names none).
- Repo upkeep: the READMEs of `ceh-vision-and-strategy` (line 28), `ceh-build-planning` (lines
  28, 58 to 59), `ceh-every-session` (lines 48, 131) and `ceh-business-plan` (lines 122 to 123,
  "A build plan in turn points to `BUSINESS_PLAN.md`", which the rule makes false), the changelog, the version bumps, and
  `docs/PLUGIN_VERSIONS.md`. The retro is committed with Phase 1 and gains a Decided section
  naming the split and this plan.

**Out:**

- The Tell skills and `whats-next` reading the business plan.: The user kept them on 2026-11-11: Tell takes only audience and positioning, and `whats-next`
  only checks that the file exists.
- An ask-first mode in `develop-business-plan` for a project that is not a business yet (retro item 4).: Not decided. It is a separate choice about the business plan suite, raised after this plan.
- Keeping kill criteria and experiments inside the plan in `run-premortem` and `find-product-market-fit` (retro item 5).: Once no build stage reads the business plan, nothing carries them out of it. A separate
  choice if a leak shows up another way.
- A grep check that fails on `BUSINESS_PLAN` in a committed document (retro item 7).: The retro defers it to a second measured miss, per the measured-miss rule.
- `find-product-market-fit` Phase 0 reading `product/plans/`.: That is the allowed direction, product documents feeding the business plan.
- Stripping the gates from Nightshift's own documents.: A change in the `ceh-nightshift` repo, not this one.
- Syncing the starlight copy of `docs/STRATEGY.md`.: `docs/starlight/scripts/sync-docs.mjs` writes `src/content/docs/`, which
  `docs/starlight/.gitignore` ignores, so there is nothing committed to sync.
- The render hook's `SPINE` entry for `BUSINESS_PLAN` in the plugins that lose the model.: The hook renders only formats whose model the plugin holds (`model_names()`), so it goes
  quiet on its own. The hook is a registered copy, and `ceh-business-plan` keeps its own.

## Design

- **Legacy key, not a format bump** `plan-model.py` keeps `business_plan: Optional[Line]` and its render line, because the model
  forbids extra keys, and a `plan/v2` plan in another repo that holds the key would fail its
  check if the field went. No skill writes it any more, so the key dies out without a
  `plan/v3`. `plan-schema.md` names the key twice. The `plan/v1` frontmatter bullet (line 32)
  reads: "`business_plan` (optional, legacy): accepted so plans written before 2026-11-11 still
  validate. No skill sets it, and no skill follows it." The `plan/v2` key list (line 78) reads
  "`business_plan` (optional, legacy, see above)". The Goal bullet loses its "With
  `business_plan` set" sentence (line 37), so every goal is a full paragraph.
- **Registry text** The "Business plan format" entry's Shared becomes: "the business plan format and its
  template. `find-product-market-fit` drafts the plan, and every specialist reads it, so each
  of the nine skills carries a copy. `ceh-blog:draft-post` and
  `ceh-seo:write-project-listing-text` read it for audience and positioning, and carry a copy
  to check `BUSINESS_PLAN.yaml` before reading it."
- **The vision skill's guard** The Rules bullet becomes: both docs are committed, so neither carries pricing, unit economics,
  kill criteria, contacts, a home path, or any test, stage, date or validation experiment from
  a business plan, and neither quotes `.agents_workspace/`. The "State the direction a business
  plan supports in your own words" sentence goes, since the skill no longer reads one. The
  Checkable goal row's Ask gains "with a measure the owner gave or the repo shows". Step 2
  drops the business plan and its `artifact.py check` sentence.
- **The rule file** `decision-business-plan-one-way.md`: "The business plan flows one way. The vision, the
  strategy and the build plans may feed it, and no skill that writes a committed product
  document (vision, strategy, build plan, decision rule, architecture) reads it. Tell may read
  it for audience and positioning, and `whats-next` for whether it exists." Why: a business
  plan turns guesses into dated tests, and a skill that reads it copies those tests into files
  later sessions treat as binding, as `product/retros/2026-11-11-39c94071-business-plan-leak.md`
  shows. It loads in every session, with no `paths`, as the other decision files do.
- **Pull requests and versions** Two phases, two PRs, each landing on its own. Phase 1 (the rule, the docs, the vision skill,
  `record-project-decisions`, the `ceh-business-plan` README and the retro):
  `ceh-vision-and-strategy` 1.1.1 to 1.1.2, `ceh-every-session` 2.9.0 to 2.9.1 and
  `ceh-business-plan` 1.2.1 to 1.2.2, PATCH for content. Phase 2 (the build plans and the plan
  format): `ceh-build-planning` 1.2.9 to 1.2.10, `ceh-build-from-plan` 1.2.6 to 1.2.7,
  `ceh-check-build-against-plan` 1.1.5 to 1.1.6, and `ceh-every-session` one PATCH further,
  because the plan-format copies sit in `whats-next` and `record-project-decisions`. The
  version numbers are those on 2026-11-11, and each PR bumps from what `main` holds then.

## Phases

### Phase 1: The one-way rule, the vision skill and record-project-decisions

- **Builds:** Scope In items 1 to 4, the orphans of item 7 for `write-vision-and-strategy` and
  `record-project-decisions`, and the upkeep of item 8 for `ceh-vision-and-strategy`,
  `ceh-every-session` and `ceh-business-plan`, with the retro committed and its Decided section
  added.
- **Check:** `git grep -nE "BUSINESS_PLAN|business-plan[-.]|business_plan"` over
  `plugins/standalone/ceh-vision-and-strategy/skills/write-vision-and-strategy/` and
  `plugins/standalone/ceh-every-session/skills/record-project-decisions/SKILL.md` prints
  nothing (the skill's plan-format copies change in Phase 2), and `test ! -e` holds for the four
  business-plan format files in each of the two skills. `git grep -n "Build and Tell read"
  .claude/rules` and `git grep -nE "build plan reads|ceh-build-planning. reads$"
  docs/STRATEGY.md` print nothing, and `docs/STRATEGY.md`'s spine-table Build row names no
  `BUSINESS_PLAN`. `git grep -n "in turn points" plugins/standalone/ceh-business-plan/README.md`
  prints nothing. `git grep -n "test, stage, date or validation experiment"` finds the vision
  skill's Rules bullet. `python tools/validate-plugins/validate.py` prints "OK: all plugin
  checks passed".
- **Status:** todo

### Phase 2: The build plans stop reading the business plan

- **Builds:** Scope In items 5 and 6, the orphans of item 7 for `write-build-plan` and `review-build-plan`,
  and the upkeep of item 8 for `ceh-build-planning`, `ceh-build-from-plan`,
  `ceh-check-build-against-plan` and `ceh-every-session`.
- **Check:** `git grep -nE "BUSINESS_PLAN|business-plan[-.]|business_plan"` over
  `plugins/standalone/ceh-build-planning/skills/` prints only `plan-model.py`'s field and render
  lines and `plan-schema.md`'s two legacy lines in each skill. With uv, `artifact.py check` exits 0
  on a scratchpad `plan/v2` YAML holding `business_plan: <path>`, and on the same file without
  it. `python tools/validate-plugins/validate.py` prints "OK: all plugin checks passed".
- **Status:** todo

## Open

None

## Record

- 2026-11-11 Planned: status ready
- 2026-11-11 Reviewed: Revise first: 1 blocking (Phase 1's grep covered record-project-decisions' plan-format copies,
  which change only in Phase 2), 7 advisory, all fixed.

<!-- prettier-ignore-end -->
