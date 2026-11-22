---
name: write-product-requirements
description: >-
  Load this skill when breaking a product into features before any is planned, even if a chat
  list or a hand edit seems enough: PRD.yaml. Trigger on "write the PRD", "break the product into
  features", "what features do we need". Not for one feature (use
  ceh-build-plan:write-build-plan).
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Checking and rendering PRD.yaml needs uv; without it the file is saved unchecked and its
  Markdown is not rendered.
license: Apache-2.0
---

# Write the product requirements

Write `PRD.yaml`, the list of features a product has or will have, so the next build plan is
picked from a list instead of from whatever seems next. Each feature carries its user, its
requirements, its acceptance criteria and its status. Done means the file passes the tests below
and its check, and is `adopted`, or `draft` with its open questions listed.

## Procedure

1. **Find what exists.** Look for `PRD.yaml` in `.agents_workspace/product/` and any path the
   repo's `CLAUDE.md` names. Run `artifact.py check` on it, per Output, and stop on exit 1 with
   its errors, unless the only error is a stale `.md`, which the render after your edit fixes.
   An existing file is revised in place: change only what the request or a finding
   needs, and keep every `id` in `features`, `non_goals` or `replaced`. A PRD or spec the user
   names in another format (a `PRD.md`, an issue, a pasted document) is input: read it, and
   never edit it.
2. **Read what the repo shows:** the vision and the strategy (`VISION.yaml` and `STRATEGY.yaml`
   in `.agents_workspace/product/`, or their `.md` in `docs/`, the root, or where `CLAUDE.md`
   says), the README, `CLAUDE.md`, the `status`, `goal` and `scope` keys of each plan YAML in
   `.agents_workspace/product/plan/`, and the code. For each `VISION.yaml` or `STRATEGY.yaml`
   that exists, run `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml`
   before reading it (formats in `${CLAUDE_SKILL_DIR}/references/vision-schema.md` and
   `strategy-schema.md`). On exit 1, stop and report its errors, because features drafted from
   a broken source carry the error. On a stale `.md` alone, read the YAML instead. On exit 2 or
   3, or without uv, say in the reply that the file went unchecked, and go on.
   Read no business plan: its dated tests would become the features' requirements.
3. **Draft the file now,** with `status: draft`, because a draft on disk survives an interrupted
   session.
   - One feature is one capability a user can observe that one build plan can deliver in its own
     pull request. A larger one splits into several.
   - List what is already built as `built`, with the plans that built it, so the list is whole.
   - Order the features so each comes after the ones it depends on, then by what the strategy's
     work rule picks first. The order is the build order.
   - A requirement states behaviour a user or caller can observe. An acceptance item is a
     statement a command or a named manual check can pass or fail.
   - What the product needs across features (speed, security, platforms) goes in
     `non_functional`. A tempting feature the product refuses goes in `non_goals` with its reason.
   - Mark every statement no source backs with `[assumed]`.
4. **Ask the owner one round of questions,** each with a recommended answer: which drafted
   features are in, which are non-goals, and each `[assumed]`. Fold the answers in and remove
   each `[assumed]` they settle. Which features a product gets is intent only the owner has.
5. **Run the tests below,** and rewrite or cut what fails.
6. **Ask the owner to confirm the file.** On their yes, set `status: adopted`. Otherwise it stays
   `draft`, because an assumption must not bind later sessions. An `adopted` file takes a change
   the owner has not confirmed only as a question.
7. **Render.** After the last edit, run `artifact.py render` on the file, per Output.

## Rules

### The tests

| Test       | Ask                                                                        | Fails when                                      |
| ---------- | -------------------------------------------------------------------------- | ----------------------------------------------- |
| Observable | Does each requirement state behaviour a user or caller can observe?        | It names an implementation                      |
| Checkable  | Can a command or a named manual check pass or fail each acceptance item?   | Nobody could tell                               |
| One plan   | Can one build plan deliver each feature in its own pull request?           | It needs several, so it splits                  |
| Traces     | Which vision goal or strategy line does each feature serve?                | None, or it is a vision non-goal                |
| Refuses    | Name one tempting feature the non-goals refuse.                            | `non_goals` is empty in a product with a vision |
| Clean      | Does the file hold pricing, dates, tests or contacts from a business plan? | It does                                         |

With no vision or strategy in the repo, mark Traces and Refuses `not run: nothing to test
against`, say so, and suggest `ceh-product-direction:write-vision-and-strategy`.

### What always holds

- Draft first, ask second. A concrete feature list the owner can correct gets a sharper answer
  than "what features do you want?".
- Set a feature's `status` and `plans` only to match plans that exist. Planning a feature is
  `ceh-build-plan:write-build-plan`'s job, and building it `ceh-build-plan:implement-from-plan`'s.
- Never reuse or renumber an `id`. A feature that is dropped moves to `non_goals` with its
  reason and keeps its `id` there, so the check refuses a later feature that takes it, because
  plans and commits name features by `id`.
- Replace a `built` feature, never rewrite it, when code built to its old requirements or
  acceptance items would fail the new ones. The new behaviour is a new feature with a new `id`.
  The old one moves to `replaced` with the successor in `replaced_by`, today's date, the reason
  and its `plans`, so `features` is always the product as it is now and the old text is not
  left beside the new.
- Each feature that depended on a replaced one names the successor, or drops the dependency
  when it no longer needs it. Move the successor before its dependants, because `depends_on`
  names only an earlier feature.
- Edit everything else in place and keep its `id`: a reworded item the old code still passes, a
  changed `name` or `user`, and any change to a `todo` or `planned` feature, because nothing is
  built to it yet. For a `planned` one, say in the reply that its plan must be revised before
  it is built.
- A `built` feature that gains a requirement stays `built`. Name the new requirement in the
  reply as work for `ceh-build-plan:write-build-plan`, which sets the feature `planned` when it
  plans it.
- `replaced` is history. Never edit an entry but to correct it, and never plan from one.
- Build skills read this file and must not read business material, so it carries no pricing,
  unit economics, kill criteria, contacts, a home path, or any test, stage or date from a
  business plan, and it never quotes `.agents_workspace/product/business/`.
- Write the YAML only. `PRD.md` is rendered from it, and the caller commits both.

## Output

`PRD.yaml` follows `${CLAUDE_SKILL_DIR}/assets/prd.template.yaml`, per
`${CLAUDE_SKILL_DIR}/references/prd-schema.md`, and goes in `.agents_workspace/product/` unless
step 1 found it elsewhere. `PRD.md` is rendered beside it and never edited by hand.

Before editing an existing file, run
`uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>` and stop on exit 1 with
its errors, unless the only one is a stale `.md`. After the last edit, run it with `render` and fix the YAML for each error it lists.
On exit 2 or 3, or without uv, say in the reply that the file went unchecked and unrendered.

Close the reply with the file's path and status, the feature table (id, name, status, depends
on), each feature replaced in this run with its successor, the result of each test, and the
open questions.

## Stop conditions

- **No human to answer** (a headless run, or called by another agent): ask nothing. Write a new
  file with `status: draft`, change nothing in an adopted file and report the proposed edits
  instead. End with the questions you would have asked, in order, each with the assumption you
  used.

## Hands off to

- To settle the technical design the features share, before the first plan, suggest
  `ceh-build-plan:write-technical-design`.
- To plan the first `todo` feature, suggest `ceh-build-plan:write-build-plan`.
