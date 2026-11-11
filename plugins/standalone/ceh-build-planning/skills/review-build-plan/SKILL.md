---
name: review-build-plan
description: >-
  Load this skill when a build plan or spec exists and nobody has built from it yet, even for a
  quick look before building: review it on scope, engineering, design, and developer experience,
  and end with a verdict. Trigger on "review this plan", "just check the phases", "review the
  spec".
argument-hint: "[plan-file]"
compatibility: >-
  Needs uv, which runs scripts/artifact.py with Python 3.10+, pydantic 2 and PyYAML to check a
  plan/v2 plan and render its Markdown, and to check a VISION or STRATEGY YAML before reading it. Without uv the plan is saved unchecked and unrendered, and those files are
  read unchecked.
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Review a Build Plan

Read a plan the way its builder will, before any code exists, and report everything that would
stop the build or send it the wrong way. A plan error caught here costs one edit. Caught in phase
four, it costs every phase built on it. Done means each applicable lens has run, every finding
quotes the plan, and the verdict is delivered.

## Procedure

1. **Find the plan.** Take the path from the arguments, or the newest plan in the plans folder
   whose status is `draft` or `ready`, and say which. The format is in
   `${CLAUDE_SKILL_DIR}/references/plan-schema.md`. With no plan but a spec (an issue, a PRD, a
   spec file), review the spec with the Scope lens and the gap checks of step 5, and skip what
   concerns phases. With neither, stop: there is nothing to review.

   **A `plan/v2` plan is checked first.** When `<slug>.yaml` sits beside the plan's `.md`, the
   YAML is the plan: read and edit it, never the `.md`. Before acting on it, run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <slug>.yaml`. When it exits 1
   with errors, stop and report them, because a stage that acts on a broken plan builds the wrong
   thing. When its only error is a stale `.md`, run the same command with `render` and go on.
   When it exits 3 or uv is missing, say in the reply that the plan went unchecked, and go on.
   After the last write to the YAML, run `render`.

2. **Review from a fresh context when this session wrote the plan.** Dispatch one background
   subagent on the most capable model with the plan path and `${CLAUDE_SKILL_DIR}/SKILL.md`, told
   to run steps 3 to 6 and return the Output. The author reads what they meant, a fresh reader
   reads what is written, and only the second is what the builder gets.
3. **Read what the plan rests on**: every file, route, model, and dependency it names in the
   repo. Read no business plan, even when an older plan links to one: the review judges
   the plan against the code, the vision and the strategy only. A plan claim the code contradicts
   is a finding. A plan claim that contradicts the repo's `VISION.md` or `STRATEGY.md`, in
   `product/`, `docs/`, the root, or where the repo's `CLAUDE.md` says, is a finding too. When a
   `VISION.yaml` or `STRATEGY.yaml` sits beside its `.md`, run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml` before reading it
   (formats in `references/vision-schema.md` and `strategy-schema.md`). On exit 1, stop and report its errors, because a review against a
   broken source judges the plan by the wrong standard. On a stale `.md` alone, read the YAML
   instead. On exit 2 or 3, or without uv, say in the reply that the file went unchecked, and go
   on.
4. **Run each lens that applies**, and name the ones you skip with the reason.

   | Lens                     | Applies                                   | Asks                                                                                                                                                                                                                                                                                                                                                     |
   | ------------------------ | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | **Scope**                | Always                                    | Does In deliver the Goal, and is each item needed now? Does the core flow need anything under Out? Is there a cheaper path to the same Goal: an installed library, an existing component, a smaller MVP?                                                                                                                                                 |
   | **Engineering**          | Always                                    | Is each phase buildable from the ones before it? Does each Check prove its phase's Builds, or only that something runs? Are timeouts, retries, duplicate requests, and partial writes designed or left open? Do the Design's types rule out illegal states, is each shared value's writer named, and does each module expose only what its callers need? |
   | **Design**               | The build has a user interface            | Does every screen in scope have its loading, error, and empty state? Does the plan say what the user sees after each action? Is the core flow as short as it can be?                                                                                                                                                                                     |
   | **Developer experience** | The callers are developers: lib, CLI, API | Can a caller reach a first working call from what the plan builds? Are names, error shapes, and defaults decided, or left to the builder? Does a breaking change get a migration path?                                                                                                                                                                   |

5. **Check the gaps every plan is checked for**, whatever the lenses: an In item no phase builds,
   a phase that builds something missing from In, a placeholder (`TODO`, `...`, "adjust as
   needed"), a name spelled two ways, a reference to a file, route, type, or field the plan never
   defines, and any Design item from `write-build-plan` step 5 that applies and is neither
   settled nor deferred.
6. **Grade each finding.** **Blocking**: the build would stop, go wrong, or build the wrong thing.
   **Advisory**: the build succeeds, but worse than it could. Then give the verdict (see Output).
7. **Fix only on request.** By default the review edits no plan content, because the plan belongs
   to its author. It appends one Reviewed entry to the plan's Record (format in the plan format
   file), as a `record` entry in a `plan/v2` YAML or a line under `## Record` in a `plan/v1`
   Markdown plan, so the review stays part of the plan's trail. A spec that is not a plan gets no
   Record line. When asked to fix, edit the plan for each blocking finding whose fix the
   plan or the code already settles, put a finding that would change In or Out under Open as a
   question with a recommended answer, and set `status: draft` while any blocking finding is open.

## Rules

- **Quote or suppress.** Every finding quotes the plan line it is about. A missing item names the
  section it belongs in. A finding you cannot anchor goes under Unverified, not in the table.
- **Judge from the plan, not the brief.** A request like "just check the phases" narrows which
  lenses run, never how severe a finding is. Say where the brief asked for less.
- Review only what is unbuilt. In a `building` plan, review the phases still `todo` or
  `unplanned`. A `built` plan is checked against its code by
  `ceh-check-build-against-plan:check-build-against-plan`, not reviewed.
- During the review, turn a question only the plan's owner can answer into a finding with a
  recommended answer.

## Output

The review fills `assets/plan-review.template.md`, per `references/plan-review-schema.md`.

| Verdict            | When                                                                               |
| ------------------ | ---------------------------------------------------------------------------------- |
| **Ready to build** | No blocking finding.                                                               |
| **Revise first**   | Blocking findings, each fixable by editing the plan.                               |
| **Rethink**        | A Scope finding changes what to build, or shows the Goal is out of reach as drawn. |

Save the whole review to `.agents_workspace/product/plan-reviews/<slug>-<YYYY-MM-DD>.md`, because the
Record line keeps only the verdict and counts, and the author fixing the plan in a later session
needs the findings. Reply with the verdict, the blocking findings, and the path.

## Hands off to

- On **Ready to build**, when `ceh-build-from-plan` is installed,
  `ceh-build-from-plan:implement-from-plan` builds the plan phase by phase.
