---
title: Every bug fix commits a fix record to product/fixes/
status: built
created: 2026-10-13
---

## Goal

Make each bug fix traceable the way a build plan makes a feature traceable. A fix skips the build
plan, because the bug already says what to build, but today its reason lives only in the chat:
`ceh-coding-conduct:find-root-cause` prints its diagnosis and saves nothing, and
`ceh-testing:test-a-bug-fix` commits only the test. After this change every fix commits
`product/fixes/<slug>.md` with the symptom, the diagnosis, the cause, and the regression tests, so a
reader who opens it later learns why the fix exists without the session that made it.

## Scope

**In:**

- A fix record format, `fix-record-format.md`, carried word for word by `find-root-cause` and
  `test-a-bug-fix` and registered in `docs/CROSS_REFERENCES.md`.
- `find-root-cause` writes the record with `status: diagnosed` once the cause is confirmed, and
  with `status: unreproduced` when the symptom never goes red. An unreproduced record is committed
  alone. (Decided by the user, 2026-10-13.)
- A diagnosed record whose fix never lands in this repo (the cause is in a dependency or the
  environment, or the fix is declined) is committed alone and stays `diagnosed`. (Decided by the
  user, 2026-10-13.)
- A record is written only when the cause is in this repo's code or config. A cause on one machine,
  or a question nobody means to fix in code, writes nothing. (Decided by the user, 2026-10-13.)
- `find-root-cause` searches `product/fixes/` for earlier records of the same behavior before it
  writes hypotheses. A match seeds a hypothesis and is linked from the new record. (Decided by the
  user, 2026-10-13.)
- A record names the built plan that delivered the broken code in an optional `plan:` field.
  (Decided by the user, 2026-10-13.)
- `test-a-bug-fix` completes the record (or creates it when the cause was known from the report),
  sets `status: fixed`, and commits it with the fix and the test.
- `docs/STRATEGY.md` lists fix records among the kept files and says when a fix needs a build plan
  instead.

**Out:**

- An entry in the build plan's Record for each fix. The user chose a separate file over writing
  into plans (2026-10-13), and the `plan:` field gives the trace in one direction.
- A validator or hook that checks a fix commit carries a record. Principle 7 asks for evidence that
  the prose fails first.
- An index of fixes. `product/fixes/` is one folder, and `ls` and grep read it.
- Records for fixes made before this change. They stay in git history.
- A row on the `docs/STRATEGY.md` spine table. No stage reads fix records as input. Only a later
  `find-root-cause` run does, and it lives outside the stages.
- Changes to `docs/TESTING_WORKFLOW.md` routing. Which skill fires when does not change.

## Design

- **Location.** `product/fixes/<slug>.md` in the target repo, committed. `product/` holds what the
  people and agents building the product read, per `docs/STRATEGY.md`. `<slug>` is kebab-case and
  names the behavior that was wrong, as the regression test does
  (`parse-duration-accepts-bare-number`), never a ticket number, because the name is what a reader
  scanning the folder sees. A taken slug gets `-2`.
- **Frontmatter.**

  ```yaml
  ---
  status: diagnosed # diagnosed | fixed | unreproduced
  date: YYYY-MM-DD
  issue: <link or ID> # omit when there is none
  plan: product/plans/<slug>.md # omit when no built plan delivered the broken code
  previous: product/fixes/<slug>.md # omit when no earlier record covers this behavior
  ---
  ```

  `plan:` is found by grepping the `status: built` plans in `product/plans/` for the file at the
  cause's `file:line`, or at the fixed `file:line` when `test-a-bug-fix` creates the record. Several
  matches take the newest by `created:`. No match, or a tie on that date, leaves it out, never
  guessed. (Tie-break decided by the user, 2026-10-13.)

- **Sections.** A title naming the wrong behavior, the Symptom line (the reproducer command and its
  failing output), Diagnosis (the hypothesis table, Cause, Prediction, as in `find-root-cause`'s
  Output), and Fix (what changed, one value line per test, what stayed unverified). When the cause
  was known from the report, Diagnosis holds one line saying so instead of the table. An
  unreproduced record's Symptom names the reported failure, its Diagnosis lists each attempt and
  what it showed, and it has no Fix section. A diagnosed record with no fix in this repo has no Fix
  section either, and its Cause names where the fix belongs (the package and version, or the
  environment setting).
- **Write only for causes in the repo.** A record is written when the cause is in this repo's code
  or config, because those are what a later reader of the repo can act on. A cause on one machine,
  or a question nobody means to fix in code ("why is CI slow"), writes nothing, so `product/` does
  not fill with debugging chats.
- **Status moves forward only.** `diagnosed` to `fixed`. `unreproduced` is final. A `diagnosed`
  record whose fix never lands here stays `diagnosed`. A later fix to the same behavior gets a new
  record whose `previous:` names the old one, so the old record stays as it was, like a built plan.
- **Who writes.** `find-root-cause` creates the record (`diagnosed` or `unreproduced`).
  `test-a-bug-fix` looks in `product/fixes/` for an uncommitted record with `status: diagnosed`
  (`git status --porcelain product/fixes/`), completes it and sets `status: fixed`, or creates one
  with `status: fixed` when there is none. Without `ceh-testing` installed, `find-root-cause`'s
  hand-off completes the record itself.
- **Prior records.** `find-root-cause` greps `product/fixes/` before step 3 for the file or function
  at the deepest frame, or, with no stack trace, for the file or function the reproducer calls. Each
  match's Cause becomes a hypothesis, and the record that matches the confirmed cause goes in
  `previous:`.
- **Same commit.** The record, the fix, and the regression test land in one commit, so
  `git log -- product/fixes/<slug>.md` finds the fix. The record carries no commit SHA, because the
  commit cannot name its own SHA. A record with no fix (`unreproduced`, or `diagnosed` with the fix
  elsewhere) is committed alone, so the investigation is not lost.
- **Shared format, no dependency.** The format is one file copied byte for byte into
  `ceh-coding-conduct/skills/find-root-cause/references/` (canonical) and
  `ceh-testing/skills/test-a-bug-fix/references/`. The hand-off between the two is conditional, so
  it stays prose with no `dependencies` entry.
- **Fix or feature.** A fix that changes a contract or the design is a feature and goes through
  `ceh-build-planning:write-build-plan`. Stated once, in `docs/STRATEGY.md`.
- **Versions.** PATCH for `ceh-coding-conduct` and `ceh-testing`: content changes, no new skill.

## Phases

### Phase 1: The fix record format

- **Builds:** `fix-record-format.md` per Design (Location, Frontmatter, Sections, Write only
  for causes in the repo, Status, Same commit), canonical in `find-root-cause/references/`, copied to `test-a-bug-fix/references/`, and
  a "Fix record format" entry in `docs/CROSS_REFERENCES.md`.
- **Check:** `diff` of the two copies prints nothing, and
  `grep -cE "^(status|plan|previous):" plugins/standalone/ceh-coding-conduct/skills/find-root-cause/references/fix-record-format.md`
  prints `3`.
- **Status:** done. `diff` of the two copies: empty. `grep -cE "^(status|plan|previous):"`: 3

### Phase 2: The two skills write the record

- **Builds:**
  - `find-root-cause`: the prior-record search before step 3, a step that saves the record with
    `status: diagnosed` only for a cause in the repo's code or config, the unreproduced stop
    condition saving it with `status: unreproduced`, the rule that a record with no fix here is
    committed alone, the dependency-cause rule pointing at that commit rule, and the hand-off
    completing the record when `ceh-testing` is not installed.
  - `test-a-bug-fix` step 6: complete or create the record and commit it with the fix and the test.
  - Whichever skill creates the record sets `plan:` per Design.
- **Check:** `grep -c "product/fixes" plugins/standalone/ceh-coding-conduct/skills/find-root-cause/SKILL.md`
  prints at least `2` (the search and the save), `grep -c "unreproduced"` on the same file prints at
  least `1`, and `grep -c "product/fixes" plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md`
  prints at least `1`. `grep -c "plan:"` prints at least `1` on both SKILL.md files. On
  `find-root-cause`, `grep -c "previous:"` and `grep -c "committed alone"` each print at least `1`.
  On `test-a-bug-fix`, `grep -c "status: fixed"` prints at least `1`.
- **Status:** done. find-root-cause: product/fixes 2, unreproduced 1, plan: 1, previous: 1,
  committed alone 2. test-a-bug-fix: product/fixes 2, plan: 1, status: fixed 1

### Phase 3: Strategy and registration

- **Builds:** the "Fix records are kept" bullet in `docs/STRATEGY.md` with the fix-or-feature rule,
  the two plugin README rows, the two `docs/CATALOG.md` rows (Find Root Cause, Test a Bug Fix),
  PATCH bumps in both `plugin.json` files and `marketplace.json`, the
  `CHANGELOG.md` 2026-10-13 section, and `docs/PLUGIN_VERSIONS.md`.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, and
  `claude plugin validate` passes for both plugins.
- **Status:** done. `validate.py`: OK: all plugin checks passed. `claude plugin validate`: ✔
  Validation passed for both

## Open

- None blocking. Assumptions taken, each open to change in review:
  - The prior-record search matches on the file or function name at the deepest frame, not on the
    symptom text, because error messages change between versions and file paths change less.
  - A taken slug gets a `-2` suffix rather than a date prefix, so the slug stays readable.
  - The review's seven findings were folded in on 2026-10-13, after the Reviewed line, with the
    user's answers on the no-fix commit rule, when to write, and the `plan:` tie-break.

## Record

- 2026-10-13 Planned: status ready. Written after a first build on branch `feat/fix-records`
  started without a plan. That branch is built against this plan, not the other way round.
- 2026-10-13 Reviewed: Revise first, 1 blocking (no terminal state or commit rule for a diagnosed
  record whose fix never lands in this repo)
- 2026-10-13 Built Phase 1: diff of the two fix-record-format.md copies empty, frontmatter field
  grep 3
- 2026-10-13 Built Phase 2: grep counts on both SKILL.md files, every required term at least 1
- 2026-10-13 Built Phase 3: validate.py, OK: all plugin checks passed
- 2026-10-13 Checked: 27 Built (7 In, 11 Design, 6 Out absent, 3 phase Checks rerun), 0 Gap,
  0 Deviation, 0 Extra
- 2026-10-13 PR: #95 https://github.com/cheneeheng/ceh-claude-code-library/pull/95
