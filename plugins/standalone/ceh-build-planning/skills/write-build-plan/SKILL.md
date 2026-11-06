---
name: write-build-plan
description: >-
  Load this skill before the first edit of a change that has no plan yet: a new app or tool, a
  feature added to existing code even when it sounds quick, or a multi-file change such as a
  retro's fixes. Writes one plan file. Trigger on "build me X", "add X to the app", "plan this".
argument-hint: "[what to build | <draft plan path>]"
compatibility: >-
  Needs uv, which runs scripts/artifact.py with Python 3.10+, pydantic 2 and PyYAML to check a
  plan/v2 plan and render its Markdown. Without uv the plan is saved unchecked and unrendered.
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Write a Build Plan

Turn a request into one plan file that an agent can build from without asking again, in the format
in `${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md`. Done means the plan is saved, audited, and
summarized under Output.

Given the path of a `plan/v2` YAML plan with `status: draft`, or of a `.md` whose frontmatter has
`generated_from: <slug>.yaml`, which resolves to that YAML, complete that plan in place. Another
step, such as a scheduler's intake, may have drafted it with only the goal and the done criteria.
Its goal and every Scope In item stay word for word, and more In items may follow them. Its Design
entries, Open items and record are kept, and step 5 adds entries after them. Its `unplanned`
phases are replaced by the phases step 6 writes. Every step still runs, and step 7 saves to the
same YAML and appends a second Planned entry after the drafter's `Planned: status draft`. A
`plan/v1` Markdown plan with no YAML beside it, or a plan that is not `draft`, is not a completable
draft: say so and write a new plan as usual.

## Procedure

1. **Triage, and announce the label in one line.**

   | Label             | The work                                                         | Path                                                  |
   | ----------------- | ---------------------------------------------------------------- | ----------------------------------------------------- |
   | **Spike**         | Throwaway code to answer one question ("can this library do X?") | No plan. Name the question and stop                   |
   | **Bounded**       | One change inside the existing design: no new component or model | A plan of one to three phases                         |
   | **Architectural** | A new app, component, data model, or major version               | A full plan. A new app gets an MVP boundary in step 3 |

   The label may move up mid-session, never down: a spike that turns into a keeper gets a plan, and
   architectural work keeps its plan when it shrinks.

2. **Read what exists before asking.** When a `VISION.md` and `STRATEGY.md` exist (in `product/`,
   `docs/`, the root, or where the repo's `CLAUDE.md` says), read them, and put anything the plan
   would contradict under Open. Read the format file, the repo, every plan in the plans
   folder that is not `built`, and only the frontmatter of each `built` one (read its full text
   only when the new work touches what it built), the README, and any issue or spec the user
   named. When `.agents_workspace/product/business/BUSINESS_PLAN.md` exists, set `business_plan` and take the goal and target
   user from it rather than restating them. Put whatever is still unclear into **one round** of
   questions, each with a recommended answer. With no human to answer, take each recommended
   answer and list it under Open.

3. **Draw the scope.** Write In and Out. For each candidate item ask: _is this needed to build
   what was asked, now?_ If not, it goes under Out with its reason. For a new app, In is the MVP:
   the smallest set that makes the app usable for its core purpose. If an item can be removed and
   the app still delivers that, it is Out.

4. **Decide how far to plan in detail.** Plan every phase in full when the build is foreseeable.
   Uncertainty, not size, cuts the detail short: a novel or unproven core mechanic, a decision
   that needs building and seeing first, or an MVP that keeps growing as you discuss it. Then plan
   in full up to the phase that settles the uncertainty, and list the rest as `unplanned`
   one-liners. Detailed phases past an open question are fiction, and building against them
   wastes more than replanning later.

5. **Write the Design.** Only the decisions the phases need, each with its reason. Settle or
   explicitly defer each of these that applies, because each one stops a builder mid-phase when
   it is left open:
   - Auth, and who owns each resource. A resource that exists but belongs to someone else returns
     the same status as a missing one, so the response does not leak that it exists.
   - Pagination on list endpoints, environment variable names, and the migration strategy.
   - Cross-origin requests: allowed origins, and the cookie policy when auth uses cookies.
   - Resources created by an explicit action, never implicitly by the first dependent action,
     which races with a second request arriving before the resource exists.
   - Loading, error, and empty states for every screen that fetches.
   - For an LLM feature: model and provider, how the message list is built from stored messages,
     and what happens when a conversation outgrows the context window.
   - For each new type, function, or module other code calls: its signature with the errors it
     returns, and the file it lives in, named for its concern and never a catch-all (`utils`).
     Then check the shape. Illegal states: name a value each type can hold that the domain
     forbids, and tighten the type or say where it is validated, once. Runs twice: say what each
     write (a row, a file, a message) does on a retry, and make it idempotent or say why it runs
     once. Shared state: name who writes each value two requests or processes touch. Smallest
     interface: a module that exposes most of what it holds hides nothing, so merge or cut it.

6. **Sequence the phases.** Foundations first (data model, auth) before the features that use
   them. No phase relies on anything a later phase introduces. Prefer thin vertical slices that
   leave the app demonstrable, but when a foundation and a slice pull against each other, the
   foundation wins. Give each phase a Check a builder can run. More than six phases is a sign to
   re-run step 4.

7. **Audit, then save.**
   - Every In item is built by some phase, and nothing a phase builds is missing from In.
   - Every phase has a runnable Check, or names its manual check and why.
   - No placeholder (`TODO`, `...`, "adjust as needed"), no reference to a file, route, type, or
     field the plan does not define, and no field named differently in two places.

   Save the plan as `plan/v2`: `<slug>.yaml` in the plans folder, a filled copy of
   `${CLAUDE_PLUGIN_ROOT}/assets/plan.template.yaml`, with `status: ready`, or `status: draft` when
   an Open question blocks building, and a Planned entry in its `record`. Then run
   `uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/artifact.py render <slug>.yaml` and fix the YAML
   for each error it lists until it exits 0, which writes `<slug>.md` beside it. Never write the
   `.md` by hand: it is generated. When the command exits 3 or uv is missing, say in the reply
   that the plan was saved unchecked and unrendered.

## Rules

- One plan per request. Leave a `built` plan as written: new work gets a new plan file. A draft
  passed by path is completed, not written again.
- Write only the plan's YAML. Its Markdown is rendered from it.
- Leave every decision that is not needed now under Out or Open, not in Design.

## Output

Close the reply with:

- The label from step 1 and the plan's YAML path.
- The In list, and the phases one line each with their Check.
- Open: every assumption taken without an answer.

## Hands off to

- For an architectural plan, `ceh-build-planning:review-build-plan` reviews it from a fresh context
  before anyone builds.
- When `ceh-build-from-plan` is installed, `ceh-build-from-plan:implement-from-plan` builds the
  plan phase by phase.
