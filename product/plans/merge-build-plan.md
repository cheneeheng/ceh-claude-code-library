---
schema: plan/v2
generated_from: merge-build-plan.yaml
generated_note: "Do not edit. artifact.py renders this file from merge-build-plan.yaml: edit the YAML, then run artifact.py render."
title: Merge ceh-build-planning and ceh-build-from-plan into ceh-build-plan
status: built
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

The plugin audit of 2026-11-11 decided that `ceh-build-planning` and `ceh-build-from-plan` become
one plugin, `ceh-build-plan`, and that `ceh-check-build-against-plan` stays its own Prove plugin.
The two Build plugins exist for one file, the `plan/v2` build plan: each registers the same hook
pair and carries the same root scripts, and each names the other as a "when installed" handoff.
It is for a user who plans a change and builds it, and installs one plugin for both. The flow
that matters most: with only `ceh-build-plan` installed, `/ceh-build-plan:write-build-plan`
saves a plan, `/ceh-build-plan:implement-from-plan` builds it, and the record guard accepts the
Built Phase line because it knows the skill under its new name.

## Scope

**In:**

- One plugin, `ceh-build-plan`, holds the three skills `write-build-plan`,
  `review-build-plan` and `implement-from-plan`, each working as before.
- One set of hooks: the generated-Markdown guard, the render hook, and the build record
  guard, which accepts a Built Phase line once `ceh-build-plan:implement-from-plan` started,
  by a Skill call or its slash command.
- The handoffs between the three skills name each other as plain next steps, with no "when
  `ceh-build-from-plan` is installed" or "when `ceh-build-planning` is installed" condition.
- One `evals/` folder holds the 37 eval cases of both plugins.
- `ceh-build-planning` and `ceh-build-from-plan` no longer exist as plugins, in the
  marketplace or in any table or list that describes the live plugins.
- Every mention of either old name in a live file names `ceh-build-plan`, proven by the
  `retired-names` check.
- The changelog tells users to uninstall the two old plugins and install the new one.

**Out:**

- Folding `ceh-check-build-against-plan` into the plugin.: Decided on 2026-11-11: it stays its own Prove plugin, so no vision change is needed.
- Any other change to what the three skills do, including `implement-from-plan` accepting a
  check the user ran, and the audit's other findings.: A merge PR that only moves and renames stays reviewable as a rename. The findings are in
  `product/plans/plugin-audit-findings.yaml`.
- New `Invoke the Skill tool` calls between the three skills.: `decision-skill-references.md` asks for an explicit call only where the procedure runs
  the skill as a step. Building after planning, and planning before building, are the
  user's next move, so they stay bare names.
- Running the eval cases.: Every run is a real model call, so it waits for a request (`decision-evaluation.md`).
- Sharing one copy of the plan model between the skills of the merged plugin.: `decision-skill-bundled-files.md` keeps a copy in each skill that reads the format.
- A copy of the old plugins under `archive/`.: Their content lives on in the new plugin, so a copy would be a second source.
- Rewriting the old names inside `product/`, `audits/`, `archive/` and `CHANGELOG.md`.: Those files are records of what was true when they were written. A plan in
  `product/plans/` that is not yet built keeps the old names, and
  `archive/README.md` maps them.

## Design

- **Depends on** Phase 1 of `product/plans/retired-names-check-and-archives.yaml`, the `retired-names` check,
  is merged before this plan is built. `product/plans/merge-session-learning.yaml` and
  `product/plans/merge-blog-and-seo.yaml` are built first, because this is the most widely
  named plugin of the four merges and the two before it prove the procedure.
- **How the plugins are merged** The base is `ceh-build-planning`, because it holds two of the three skills.

  1. `git mv plugins/standalone/ceh-build-planning plugins/standalone/ceh-build-plan`.
  2. `git mv plugins/standalone/ceh-build-from-plan/skills/implement-from-plan
     plugins/standalone/ceh-build-plan/skills/`,
     `git mv plugins/standalone/ceh-build-from-plan/scripts/build-record-guard.py
     plugins/standalone/ceh-build-plan/scripts/`, and `git mv` each of the 17 case folders
     under `plugins/standalone/ceh-build-from-plan/evals/` into
     `plugins/standalone/ceh-build-plan/evals/`. No case name collides: the base's cases open
     with `rbp-` or `wbp-`.
  3. Fold what `ceh-build-from-plan/README.md` says into the new README, which gets one table
     of the three skills and keeps the hook, uv and environment variable notes of both, then
     `git rm -r plugins/standalone/ceh-build-from-plan`. Its three other root scripts are
     byte-identical copies of the base's, so nothing is lost.
  4. `plugin.json`: `name` becomes `ceh-build-plan`, `description` covers planning and
     building in one sentence, `keywords` are the union, and `version` is the next MAJOR of
     the base plugin's version at build time (`2.0.0` from `1.x`), per
     `decision-version-levels.md`. The base's `tuning.json` moves with the folder and the
     other is deleted with its plugin.
  5. `.claude-plugin/marketplace.json`: the two old entries become one, mirroring
     `plugin.json`.
  6. Add both old names to `RENAMED` in `tools/validate-plugins/checks/retired_names.py`,
     each mapped to `ceh-build-plan`.
  7. Run `python tools/validate-plugins/validate.py` and edit every file it lists until it is
     green. A mention that states the present is edited, and a mention that states history
     stays and its file is added to `ALLOWED`.
- **Hooks** `hooks/hooks.json` becomes the one `ceh-build-from-plan` has today: on `PreToolUse` for
  `Edit|Write|MultiEdit`, `build-record-guard.py` then `generated-md-guard.py`, and on
  `PostToolUse`, `artifact-render-hook.py`, with the same timeouts.
  `scripts/build-record-guard.py` holds the skill's name in its `STARTED` pattern (twice)
  and in its `REASON` text (twice). All four become `ceh-build-plan:implement-from-plan`, or
  the guard denies every Built Phase line.
- **The validator** In `tools/validate-plugins/checks/hooks.py`: the two transcript fixtures that hold
  `ceh-build-from-plan:implement-from-plan` take the new name, and
  `artifact_fixtures("ceh-build-planning", True)` and
  `artifact_fixtures("ceh-build-from-plan", False)` become one call for `ceh-build-plan`. In
  `tools/validate-plugins/checks/artifact_models.py`, the `CLI` path takes the new folder
  name. `NAMES_TO_DETECT` in `checks/repo_rules.py` lists script names, so it stays.
- **Handoffs between the three skills** `write-build-plan` ends "Hands off to" with `ceh-build-plan:implement-from-plan` builds the
  plan phase by phase, with no "when installed". `review-build-plan`'s handoff is reworded
  the same way. `implement-from-plan` names `ceh-build-plan:write-build-plan` without its
  "when `ceh-build-planning` is installed" condition. Its handoffs to `ceh-testing` and to
  `ceh-check-build-against-plan:check-build-against-plan` keep "when installed", because
  those plugins stay separate. The paragraph "A `plan/v2` plan is checked first" stays in
  each skill that has it.
- **The plan schema and its copies** `plan-schema.md` names `ceh-build-planning` and `ceh-build-from-plan` in its first
  paragraph and is copied word for word into every skill that reads a plan: six copies today,
  in the two merging plugins, `ceh-check-build-against-plan` and `ceh-every-session`.
  The canonical copy is edited first and mirrored to every copy listed in
  `docs/CROSS_REFERENCES.md`, and the `copies` check proves they match. Every registered
  path under either old folder in `docs/CROSS_REFERENCES.md` takes the new folder name.
- **Files that name the old plugins** Known today, and the check in step 7 finds any other. Docs and rules: `CLAUDE.md` (tier
  table and the Evaluation section), `README.md`, `docs/CATALOG.md`,
  `docs/CROSS_REFERENCES.md`, `docs/ENVIRONMENT_VARIABLES.md` (the `CEH_BUILD_RECORD_GUARD`,
  `CEH_ARTIFACT_CHECK` and `CEH_DISABLED_HOOKS` rows), `docs/GETTING_STARTED.md`,
  `docs/IDEAS.md`, `docs/PLUGIN_DEPENDENCIES.md` (three rows), `docs/PLUGIN_VERSIONS.md` (two
  rows become one), `docs/RETRO_WORKFLOW.md`, `docs/STRATEGY.md` (the stage table, the
  "Build planning belongs to Build" paragraph, the Shape to Build paragraph, and the fix
  record and retro bullets), `docs/VISION.md` (the Build row), `plugins/CLAUDE.md`, and
  `.claude/rules/decision-artifact-validation.md`. Skill bodies and READMEs in other
  plugins: `ceh-business-plan` (its README, the bodies of `develop-business-plan`,
  `find-product-market-fit` and `set-operating-plan`, which name the plugin on its own, and
  the nine copies of `business-plan-schema.md`, edited in the canonical copy first),
  `ceh-check-build-against-plan`, `ceh-every-session`, `ceh-git-workflow` (`pull-request`
  and `review-recent-work`), `ceh-testing` (`write-evidence-report`),
  `ceh-vision-and-strategy`, `ceh-coding-conduct` (README), `ceh-codebase-explanation`,
  `ceh-documentation`, `ceh-python-service`, and the plugins the earlier merges produced,
  `ceh-blog-and-seo` and `ceh-session-learning`. The eval cases are searched too, since a
  prompt or grader may hold the old name.
- **Version bumps in other plugins** Every other plugin whose files change gets a PATCH bump in `plugin.json` and
  `marketplace.json`, a row in the changelog's `### Plugin versions` table, and its row in
  `docs/PLUGIN_VERSIONS.md`. The list is the plugins under "Files that name the old
  plugins", as the check in step 7 confirms it.
- **The vision's stage table** The PR replaces the two old names with `ceh-build-plan` in the stage tables of
  `docs/VISION.md` and `docs/STRATEGY.md`. `decision-vision-governs.md` says a file and the
  vision that disagree are fixed in the same PR. Both plugins are in the Build row, so no
  principle, goal or scope test changes, and the changelog entry says the table was edited
  and why.
- **The changelog entry** Under the PR's date: prose on the merge and its reason, the `### Plugin versions` table,
  and under `### Changed` the line for users: uninstall `ceh-build-planning` and
  `ceh-build-from-plan`, install `ceh-build-plan`, and the three skills keep their names
  under the new prefix. It also says that a session started before the reinstall still runs
  the old plugins from its cache.

## Phases

### Phase 1: Merge into ceh-build-plan

- **Builds:** "How the plugins are merged", steps 1 to 7, with "Hooks", "The validator", "Handoffs
  between the three skills", "The plan schema and its copies", "Files that name the old
  plugins", "Version bumps in other plugins", "The vision's stage table" and "The changelog
  entry". One PR.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, which
  includes the build record guard's fixtures under the new skill name and the `copies` check
  on the plan schema. `claude plugin validate plugins/standalone/ceh-build-plan` passes.
  `ls plugins/standalone/ceh-build-plan/skills` lists the three skills,
  `ls plugins/standalone/ceh-build-plan/evals` lists 37 case folders, and neither old folder
  exists. CI is green on the PR.
- **Status:** done, Commit de4c279. `python tools/validate-plugins/validate.py` printed
  `OK: all plugin checks passed`. `claude plugin validate plugins/standalone/ceh-build-plan`
  printed `Validation passed`. `skills/` lists the three skills, `evals/` holds 37 case
  folders, and neither old folder exists. CI run 43202288693 on PR #262 succeeded. Both old plugins had a git-ignored `evals/results/` folder of local eval run output. The
  base's moved with its folder. The one under `ceh-build-from-plan` was deleted with that
  folder during the build and could not be restored, since git never tracked it.
  Not covered by a command: loading the plugin in a fresh session with
  `claude --plugin-dir plugins/standalone/ceh-build-plan` and seeing the three skills listed,
  and a run of the eval cases. The builder reports both as not run unless the user asks.

## Open

- The session that builds this plan runs the installed `ceh-build-from-plan`, whose record
  guard expects the old skill name. Does that block recording the phase?: No. The installed copy in the plugin cache is unchanged by the PR, so the builder starts
  `ceh-build-from-plan:implement-from-plan` as installed and the guard accepts the Built
  Phase line. The new name applies after the user reinstalls.
- May the merge PR edit the stage tables in `docs/VISION.md`, or does that need its own PR
  first?: It may, per "The vision's stage table".

## Record

- 2026-11-12 Planned: status ready
- 2026-11-12 PR: #258 https://github.com/cheneeheng/ceh-claude-code-library/pull/258
- 2026-11-12 Built Phase 1: `ceh-build-planning` and `ceh-build-from-plan` merged into `ceh-build-plan` 2.0.0, with the
  three-hook `hooks.json`, the record guard on the new skill name, the handoffs reworded, the
  six plan schema copies edited, and every plugin that named either old plugin bumped. Built
  in one PR with the three other merge plans, at the user's request.
- 2026-11-12 PR: #262 https://github.com/cheneeheng/ceh-claude-code-library/pull/262

<!-- prettier-ignore-end -->
