---
schema: plan/v2
generated_from: merge-product-direction.yaml
generated_note: "Do not edit. artifact.py renders this file from merge-product-direction.yaml: edit the YAML, then run artifact.py render."
title: Merge ceh-vision-and-strategy into ceh-business-plan as ceh-product-direction
status: ready
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

The plugin audit of 2026-11-11 decided that `ceh-vision-and-strategy` merges into
`ceh-business-plan`, and that the result is named `ceh-product-direction`. Both are Shape, both
decide what to build and whether it is worth it, and since PR 253 the business plan also covers
a project that is not a business, so the two serve the same repos. It is for a user who reaches
Shape and installs one plugin for it. The flow that matters most: with only
`ceh-product-direction` installed, `/ceh-product-direction:write-vision-and-strategy` writes
`product/VISION.yaml` and `product/STRATEGY.yaml` without reading the business plan, and
`/ceh-product-direction:develop-business-plan` routes to its eight specialists beside it.

## Scope

**In:**

- One plugin, `ceh-product-direction`, holds `write-vision-and-strategy`,
  `develop-business-plan` and the eight model-only specialists, each working as before.
- The plugin's one pair of artifact hooks checks and renders the vision, the strategy and the
  business plan.
- The plugin's README states that `write-vision-and-strategy` never reads the business plan,
  citing `decision-business-plan-readers.md`.
- `write-vision-and-strategy`'s description stays within 300 characters with its "Not for"
  pointer naming `ceh-product-direction:develop-business-plan`.
- `ceh-vision-and-strategy` and `ceh-business-plan` no longer exist as plugins, in the
  marketplace or in any table or list that describes the live plugins.
- Every mention of either old name in a live file names `ceh-product-direction`, proven by
  the `retired-names` check.
- The changelog tells users to uninstall the two old plugins and install the new one.

**Out:**

- Any other change to what the ten skills do, including the audit's findings on them.: A merge PR that only moves and renames stays reviewable as a rename. The findings are in
  `product/plans/plugin-audit-findings.yaml`.
- A `validate.py` check that the vision writer never reads the business plan.: Both skills already carry the rule in their text, and no session has shown it failing
  (vision principle 7). The README states it.
- Merging `ceh-competitor-analysis` into the plugin.: Rejected in the audit while it depends on `ceh-ui-design`.
- Sharing one copy of a model between the skills of the merged plugin.: `decision-skill-bundled-files.md` keeps a copy in each skill that reads the format.
- A copy of the old plugins under `archive/`.: Their content lives on in the new plugin, so a copy would be a second source.
- Rewriting the old names inside `product/`, `audits/`, `archive/` and `CHANGELOG.md`.: Those files are records of what was true when they were written.

## Design

- **Depends on** Phase 1 of `product/plans/retired-names-check-and-archives.yaml`, the `retired-names` check,
  is merged before this plan is built. `product/plans/merge-build-plan.yaml` is built first,
  because both plans edit the business plan skills and this one then moves files that plan
  has already edited.
- **How the plugins are merged** The base is `ceh-business-plan`, because it holds nine of the ten skills and the HTML
  generator.

  1. `git mv plugins/standalone/ceh-business-plan plugins/standalone/ceh-product-direction`.
  2. `git mv plugins/standalone/ceh-vision-and-strategy/skills/write-vision-and-strategy
     plugins/standalone/ceh-product-direction/skills/`.
  3. Fold what `ceh-vision-and-strategy/README.md` says into the new README, which gets one
     table of the ten skills, names the two entry points (`write-vision-and-strategy` and
     `develop-business-plan`), and states the reader rule under "The reader rule" below, then
     `git rm -r plugins/standalone/ceh-vision-and-strategy`. Its `hooks/hooks.json` and three
     root scripts are byte-identical copies of the base's, so nothing is lost.
  4. `plugin.json`: `name` becomes `ceh-product-direction`, `description` covers both uses in
     one sentence, `keywords` are the union, and `version` is the next MAJOR of the base
     plugin's version at build time (`2.0.0` from `1.x`), per `decision-version-levels.md`.
     The base's `tuning.json` moves with the folder and the other is deleted with its plugin.
  5. `.claude-plugin/marketplace.json`: the two old entries become one, mirroring
     `plugin.json`.
  6. Add both old names to `RENAMED` in `tools/validate-plugins/checks/retired_names.py`,
     each mapped to `ceh-product-direction`.
  7. Run `python tools/validate-plugins/validate.py` and edit every file it lists until it is
     green. A mention that states the present is edited, and a mention that states history
     stays and its file is added to `ALLOWED`.
- **The reader rule** The README says, in its own short section: `write-vision-and-strategy` never reads the
  business plan, the business plan may read the vision and the strategy, and the reason is in
  `.claude/rules/decision-business-plan-readers.md`. The skill's own sentence "Read no
  business plan" stays as written. `develop-business-plan`'s description keeps calling it the
  single entry point for a business plan, which stays true.
- **The description of write-vision-and-strategy** It is 299 characters today and its "Not for" pointer names
  `ceh-business-plan:develop-business-plan`. The new prefix is four characters longer, so
  the description is reworded to fit 300 with the pointer kept, by shortening its trigger
  phrases and nothing else. This is the one content edit the merge needs.
- **The validator** In `tools/validate-plugins/checks/hooks.py`, the fixture groups for
  `ceh-vision-and-strategy` (`VISION`) and `ceh-business-plan` (`BUSINESS_PLAN`) both run
  against `ceh-product-direction`, and stay two groups because they test two formats.
- **Files that name the old plugins** Known today, and the check in step 7 finds any other: `CLAUDE.md` (tier table),
  `README.md`, `docs/CATALOG.md`, `docs/CROSS_REFERENCES.md` (every registered path under
  either old folder, among them the business plan model set, the vision and strategy models
  copied into `ceh-build-plan`, and the Meridian `brand.css` copy),
  `docs/ENVIRONMENT_VARIABLES.md`, `docs/GETTING_STARTED.md`, `docs/IDEAS.md`,
  `docs/PLUGIN_DEPENDENCIES.md`, `docs/PLUGIN_VERSIONS.md` (two rows become one),
  `docs/STRATEGY.md` (the stage table and the Shape to Build paragraph), `docs/VISION.md`
  (the Shape row), `plugins/CLAUDE.md` and `.claude/rules/decision-skill-bundled-files.md`
  (the allowed script bundle), `.claude/rules/decision-artifact-validation.md`, and the
  READMEs of `ceh-build-plan` and `ceh-competitor-analysis`. Inside the plugin, every
  `ceh-business-plan:<skill>` name in a skill body, reference file or script takes the new
  prefix, the router's `Invoke the Skill tool` lines among them.
- **Version bumps in other plugins** Every other plugin whose files change gets a PATCH bump in `plugin.json` and
  `marketplace.json`, a row in the changelog's `### Plugin versions` table, and its row in
  `docs/PLUGIN_VERSIONS.md`. Known today: `ceh-build-plan` and `ceh-competitor-analysis`. A
  file registered in `docs/CROSS_REFERENCES.md` is edited in its canonical copy first and
  mirrored to every copy.
- **The vision's stage table** The PR replaces the two old names with `ceh-product-direction` in the stage tables of
  `docs/VISION.md` and `docs/STRATEGY.md`. `decision-vision-governs.md` says a file and the
  vision that disagree are fixed in the same PR. Both plugins are in the Shape row, so no
  principle, goal or scope test changes, and the changelog entry says the table was edited
  and why.
- **The changelog entry** Under the PR's date: prose on the merge and its reason, the `### Plugin versions` table,
  and under `### Changed` the line for users: uninstall `ceh-vision-and-strategy` and
  `ceh-business-plan`, install `ceh-product-direction`, and the ten skills keep their names
  under the new prefix. It also says what a vision-only user now carries: nine more
  descriptions in the skill listing.

## Phases

### Phase 1: Merge into ceh-product-direction

- **Builds:** "How the plugins are merged", steps 1 to 7, with "The reader rule", "The description of
  write-vision-and-strategy", "The validator", "Files that name the old plugins", "Version
  bumps in other plugins", "The vision's stage table" and "The changelog entry". One PR.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, which
  includes the vision and business plan hook fixtures under the new folder name and the
  300-character limit on the reworded description.
  `claude plugin validate plugins/standalone/ceh-product-direction` passes.
  `ls plugins/standalone/ceh-product-direction/skills` lists ten skills, neither old folder
  exists, and `ls plugins/standalone` lists 21 plugins. CI is green on the PR.
- **Status:** todo. Not covered by a command: loading the plugin in a fresh session with
  `claude --plugin-dir plugins/standalone/ceh-product-direction` and seeing the two entry
  points listed. The builder reports it as not run unless the user asks for it.

## Open

- May the merge PR edit the stage tables in `docs/VISION.md`, or does that need its own PR
  first?: It may, per "The vision's stage table".

## Record

- 2026-11-12 Planned: status ready
- 2026-11-12 PR: #258 https://github.com/cheneeheng/ceh-claude-code-library/pull/258

<!-- prettier-ignore-end -->
