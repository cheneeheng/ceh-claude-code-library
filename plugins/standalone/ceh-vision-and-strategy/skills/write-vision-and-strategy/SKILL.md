---
name: write-vision-and-strategy
description: >-
  Load this skill when a repo's direction must be written down to settle later decisions:
  VISION.md and STRATEGY.md, drafted from the repo, then confirmed with its owner. Trigger on "write
  the vision doc", "create a strategy doc". Not for a business plan (use
  ceh-business-plan:develop-business-plan).
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Checking and rendering VISION.yaml and STRATEGY.yaml needs uv; without it the files are saved
  unchecked and their Markdown is not rendered.
license: Apache-2.0
---

# Write the vision and strategy

Write the two files that let a later session settle a decision without asking: `VISION.md`, why the
repo exists and which principles decide, and `STRATEGY.md`, how it gets there and how work is chosen.
Done means both pass the tests below, and each is `adopted` with a pointer from `CLAUDE.md`, or
`draft` with its open questions listed. The repo may hold code or only documents. Read it the same
way.

## Procedure

1. **Find what exists.** Look for each doc in `product/`, `docs/`, the root, and any path the repo's
   `CLAUDE.md` names. An existing doc stays where it is and is revised: change only what the request
   or a finding needs, and keep the owner's wording. A request for one doc when the other is missing
   drafts both, because the two hold up against each other. An existing Markdown doc is moved to
   its YAML first, per Output: one with no `schema:` line gets `status: adopted` when the repo's
   `CLAUDE.md` or the owner already treats it as binding, otherwise `draft`. Its sections outside
   the template go in `extra_sections`, and a required field it lacks reads "Not stated yet." until
   a later step writes to it, so an adopted doc stays adopted through the move.
2. **Read what the repo shows:** the README, `CLAUDE.md`, `.claude/rules/`, plans, any architecture,
   ideas, or roadmap file, the changelog, and recent `git log`. Read no business plan: the vision
   feeds it, never the reverse, because its dated tests would become the docs' goals. When what
   the repo does and what it claims differ, what it does is the evidence.
3. **Draft each doc that does not exist, now,** with `status: draft`, because a draft on disk survives
   an interrupted session. Mark every statement of intent no source backs with `[assumed]`. An
   `adopted` doc stays `adopted` and never gets an `[assumed]`: a change the owner has not confirmed
   goes to step 4 as a question, and is written only once they confirm it.
4. **Interview the owner,** one question per turn, each offering the draft's hypothesis to correct, in
   this order of worth: who it is for, the end state, what it refuses, which principle wins a
   conflict. Fold each answer in and remove its `[assumed]`. Stop when none remain or after eight
   questions. Intent nobody wrote down is a fact only the owner has, which is why this skill
   interviews. Ask nothing else except the confirmation in step 7.
5. **Run the tests below on both docs,** and rewrite or cut what fails. In a repo too new to supply
   decisions, candidates, or parts, take them from the owner's upcoming decisions, or from the docs'
   own Goals.
6. **Record each difference** between the docs and the repo under Where the repo does not match yet.
   Fix nothing in the repo.
7. **Ask the owner to confirm the docs,** listing each remaining `[assumed]` to confirm or correct. On
   their yes, set `status: adopted`, and add one pointer to the repo's `CLAUDE.md`, creating it if
   missing and unless one already points at these docs: read these docs before changing direction,
   and every change holds up against them. Otherwise the doc stays `draft` with no pointer, because
   an assumption must not bind later sessions.

## The tests

| Test           | Ask                                                                                              | Fails when                                                       |
| -------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Opposite       | Would a sane project choose the opposite of each principle or non-goal?                          | Nobody would: "high quality" and "user-focused" are not choices  |
| Past decision  | Take two real decisions from the plans, ideas, or history. Does the doc settle them?             | It settles neither, so the doc only decorates the repo           |
| Rejected item  | Name one tempting thing the scope test refuses.                                                  | The test refuses nothing                                         |
| Checkable goal | How would someone tell each goal is met or not, with a measure the owner gave or the repo shows? | Nobody could tell                                                |
| Reason         | Could a reader apply each principle to a case the text does not cover?                           | The principle has no reason                                      |
| Strategy adds  | Which strategy lines say how, not what the vision already says?                                  | The strategy restates the vision                                 |
| Chooses work   | Give the work rule two real candidates. Does it pick one?                                        | It accepts both or neither with no reason                        |
| Fits the repo  | Does each major part of the repo appear in The parts?                                            | A part appears nowhere, or the doc names one that does not exist |

## Rules

- Draft first, ask second. A concrete sentence the owner can correct gets a sharper answer than "what
  is your vision?".
- Both docs are committed, so neither carries pricing, unit economics, kill criteria, contacts, a
  home path, or any test, stage, date or validation experiment from a business plan, and neither
  quotes `.agents_workspace/`.
- Write files only. The caller commits them.

## Output

`VISION.yaml` follows `assets/vision.template.yaml`, per the `vision/v2` section of
`references/vision-schema.md`, and `STRATEGY.yaml` follows `assets/strategy.template.yaml`, per the
`strategy/v2` section of `references/strategy-schema.md`. `VISION.md` and `STRATEGY.md` are
rendered from them in the layouts of `assets/vision.template.md` and `assets/strategy.template.md`,
and never edited by hand. Both go in `product/` unless step 1 found them elsewhere, and each YAML
sits beside its Markdown. An existing Markdown file with no YAML beside it is moved first, as the
schema says.

Before editing a YAML, run `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>`
and stop on exit 1 with its errors. After the last edit, run it with `render` and fix the YAML for
each error it lists. On exit 2 or 3, or without uv, say in the reply that the file went unchecked
and unrendered. Close the reply with each file's path and status, the result of each test, and the
open questions.

## Stop conditions

- **No human to answer** (a headless run, or called by another agent): ask nothing. Write new docs
  with `status: draft`, add no pointer, change nothing in an adopted doc and report its proposed edits
  instead, and mark any test with nothing to run against `not run: nothing to test against`. End with
  the questions you would have asked, in order, each with the assumption you used.

## Hands off to

- To question the finished docs, suggest `ceh-every-session:stress-test-plan`.
- To plan the first piece of work they choose, suggest `ceh-build-plan:write-build-plan`.
