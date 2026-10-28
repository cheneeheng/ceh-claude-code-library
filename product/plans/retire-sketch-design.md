---
schema: plan/v1
title: Move sketch-design's checks into planning, then retire it and its guard
status: built
created: 2026-10-28
---

## Goal

Apply the `sketch-design` row of the keep-or-merge table in
`product/retros/2026-10-28-repeat-mistake.md`, approved by the user on 2026-10-28. The four shape
checks (illegal states, runs twice, shared state, smallest interface) run where the shape is
decided, in a plan's Design, and are reviewed there. `ceh-coding-conduct:sketch-design` and the
`ceh-coding-conduct` copy of `skill-started-guard.py` are removed, and nothing names them.

## Scope

**In:**

- `write-build-plan` step 5 settles the shape of each new type, function, or module other code
  calls: its signature, the four checks, and the file it lives in.
- `review-build-plan`'s Engineering lens asks whether the Design's types and modules pass those
  checks.
- `ceh-build-from-plan:implement-from-plan` step 3.1 takes the shape from the plan's Design instead
  of naming `sketch-design`, and settles it in the Design first when the Design does not (an older
  plan, or the minimal plan its step 1 writes).
- `ceh-coding-conduct` loses `skills/sketch-design/`, `scripts/skill-started-guard.py`, and its
  `PreToolUse` entry in `hooks/hooks.json`.
- The remaining two copies of `skill-started-guard.py` (`ceh-git-workflow`, `ceh-testing`) drop the
  `new_source` branch of `subject()`, which no `RULES` row uses once the third copy is gone.
- Every reference is updated: `docs/CATALOG.md`, the root `README.md` Plugins row, the
  `ceh-coding-conduct` README, the `ceh-coding-conduct` description in its `plugin.json` and in
  `.claude-plugin/marketplace.json` ("sketching the design before the code"), the
  `ceh-coding-conduct` row of `docs/GETTING_STARTED.md` ("design before code"),
  `docs/CROSS_REFERENCES.md` (the kill-switch row and the guard-copy row for `ceh-coding-conduct`,
  and the Shared line's `new_source` mention), `docs/ENVIRONMENT_VARIABLES.md`, the "new source"
  wording in the `NAMES_TO_DETECT` comment of `tools/validate-plugins/checks/repo_rules.py`, and in
  `tools/validate-plugins/checks/hooks.py` the `cc` fixtures with their `cc` and `new_src`
  definitions.
- The retro records the outcome of all five keep-or-merge rows.

**Out:**

- Retiring `commit` or `update-changelog`: the user keeps both, with the guard enforcing them.
- `docs/IDEAS.md`'s "Design sketch before code" row: it records where an idea came from, not what
  ships.
- `plan-schema.md`: step 5 is the Design checklist, and `review-build-plan` step 5 already checks
  every step-5 item, so the schema needs no change.
- `CHANGELOG.md` entries, `product/` records, and `audits/` reports that name `sketch-design`:
  history stays as written.
- Generated `docs/starlight/` content: `sync-docs.mjs` rebuilds it from the tracked docs.

## Design

- The new step-5 bullet is written for code only ("for each new type, function, or module other
  code calls"), so a plan for a docs-only repo skips it under "each of these that applies".
- The Engineering cell gains one question rather than four: duplicate requests and partial writes
  already cover "runs twice", so the addition is illegal states, who writes shared state, and the
  smallest interface.
- `sketch-design`'s "one concern per file, named for it, never a catch-all" rule moves with the
  checks into the same bullet, as the file the shape lives in. Its "do not sketch what nobody asked
  for" rule is already `write-less-code` rung 1.
- Without its `new_source` branch, `subject()` returns the command for `command` and the path for
  every other kind: the `if kind == "path"` test goes, so no kind falls through to `None`.
- Versions: `ceh-build-planning` PATCH (content), `ceh-build-from-plan` PATCH, `ceh-coding-conduct`
  MINOR (a skill and a hook removed, the counterpart of adding one), `ceh-git-workflow` and
  `ceh-testing` PATCH (dead branch removed).
- Two staged PRs, so planning holds the checks before the skill goes: PR 1 is Phase 1, PR 2 is
  Phase 2.

## Phases

### Phase 1: Put the checks in planning

- **Builds:** the `write-build-plan` step-5 bullet, the `review-build-plan` Engineering question,
  the `ceh-build-planning` PATCH bump, changelog and versions rows, and this plan committed.
- **Check:** `python tools/validate-plugins/validate.py` shows no failure outside git-ignored
  files, and `grep -n -i "illegal" plugins/standalone/ceh-build-planning/skills/*/SKILL.md` finds
  both skills.
- **Status:** done. `validate.py` reports 25 problems, all in git-ignored `docs/starlight/node_modules/`
  or `evals/results/`, 0 elsewhere; the grep finds one line in each skill.

### Phase 2: Retire sketch-design and its guard

- **Builds:** the deletions in `ceh-coding-conduct`, the `implement-from-plan` step 3.1 rewording,
  the `new_source` branch removed from both remaining guard copies, the `cc` fixtures removed from
  `hooks.py`, every doc row in In, the retro update, the four version bumps, changelog and versions
  rows.
- **Check:** `python tools/validate-plugins/validate.py` as in Phase 1,
  `python tools/validate-plugins/checks/hooks.py` passes, the two guard copies match outside
  `RULES`, and
  `git grep -n -i -E "sketch|design before code|new_source|new source" -- plugins tools docs README.md .claude-plugin ':!docs/IDEAS.md' ':!docs/starlight'`
  finds nothing outside `ceh-git-datastore`'s unrelated "TypeScript sketch".
- **Status:** done. `validate.py` has 0 problems outside git-ignored files, `checks/hooks.py` prints
  "OK: hooks check passed", the two guard copies match outside `RULES`, and the grep finds only the
  two `ceh-git-datastore` "TypeScript sketch" lines. `implement-from-plan` names the checks inline
  rather than pointing at `write-build-plan`, because `ceh-build-from-plan` must work without
  `ceh-build-planning` installed. The plugin's `hooks.py` fixture setup for `guarded/src/` went with
  the `cc` fixtures it served.

## Open

- Removing a skill has no versioning rule in `CLAUDE.md`. Assumed MINOR, the counterpart of adding
  one, since MAJOR is for a renamed or removed plugin.

## Record

- 2026-10-28 Planned: status ready
- 2026-10-28 Reviewed: Revise first, 1 blocking
- 2026-10-28 Revised: all 5 findings fixed in the plan
- 2026-10-28 Built Phase 1: `python tools/validate-plugins/validate.py`, 0 problems outside git-ignored files
- 2026-10-28 PR: #176 https://github.com/cheneeheng/ceh-claude-code-library/pull/176
- 2026-10-28 Built Phase 2: `python tools/validate-plugins/checks/hooks.py`, OK: hooks check passed
- 2026-10-28 Checked: 20 Built, 0 Gap, 0 Deviation, 0 Extra, 0 Failing
- 2026-10-28 PR: #177 https://github.com/cheneeheng/ceh-claude-code-library/pull/177
