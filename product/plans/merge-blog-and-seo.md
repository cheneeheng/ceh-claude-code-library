---
schema: plan/v2
generated_from: merge-blog-and-seo.yaml
generated_note: "Do not edit. artifact.py renders this file from merge-blog-and-seo.yaml: edit the YAML, then run artifact.py render."
title: Merge ceh-blog and ceh-seo into ceh-blog-and-seo
status: ready
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

The plugin audit of 2026-11-11 decided that `ceh-blog` and `ceh-seo` become one plugin,
`ceh-blog-and-seo`. The two are the whole Tell stage, and `draft-post` and
`write-project-listing-text` read the same two handoff files, the business plan and the evidence
report, through copies of the same two models. It is for a user who reaches Tell and installs
one plugin for it. The flow that matters most: with only `ceh-blog-and-seo` installed,
`/ceh-blog-and-seo:draft-post` saves a checked voice profile through the plugin's hooks, and
`/ceh-blog-and-seo:write-project-listing-text` reads the same evidence report beside it.

## Scope

**In:**

- One plugin, `ceh-blog-and-seo`, holds the six skills `draft-post`, `edit-post`,
  `repurpose-post`, `make-page-crawlable`, `write-llms-txt` and `write-project-listing-text`,
  each working as before.
- The plugin's one pair of artifact hooks still checks and renders the blog voice profile and
  the evidence report, as `ceh-blog`'s hooks do today.
- `ceh-blog` and `ceh-seo` no longer exist as plugins, in the marketplace or in any table or
  list that describes the live plugins.
- Every mention of either old name in a live file names `ceh-blog-and-seo`, proven by the
  `retired-names` check.
- The changelog tells users to uninstall the two old plugins and install the new one.

**Out:**

- Any change to what the six skills do, including the audit's findings on them.: A merge PR that only moves and renames stays reviewable as a rename. The findings are in
  `product/plans/plugin-audit-findings.yaml`.
- Sharing one copy of a model between two skills of the merged plugin.: `decision-skill-bundled-files.md` keeps a copy in each skill that reads the format.
- A copy of the old plugins under `archive/`.: Their content lives on in the new plugin, so a copy would be a second source.
- Rewriting the old names inside `product/`, `audits/`, `archive/` and `CHANGELOG.md`.: Those files are records of what was true when they were written.

## Design

- **Depends on** Phase 1 of `product/plans/retired-names-check-and-archives.yaml`, the `retired-names` check,
  is merged before this plan is built. `product/plans/merge-session-learning.yaml` is built
  first, because it proves the procedure on the smallest case.
- **How the plugins are merged** The base is `ceh-blog`, because it holds the hooks and the root scripts.

  1. `git mv plugins/standalone/ceh-blog plugins/standalone/ceh-blog-and-seo`.
  2. `git mv` each of the three skill folders under `plugins/standalone/ceh-seo/skills/` into
     `plugins/standalone/ceh-blog-and-seo/skills/`.
  3. Fold what `ceh-seo/README.md` says into the new README, which gets one table of all six
     skills and keeps the hook and uv notes, then `git rm -r plugins/standalone/ceh-seo`.
  4. `plugin.json`: `name` becomes `ceh-blog-and-seo`, `description` covers both uses in one
     sentence, `keywords` are the union, and `version` is the next MAJOR of the base plugin's
     version at build time (`2.0.0` from `1.x`), per `decision-version-levels.md`. The base's
     `tuning.json` moves with the folder and the other is deleted with its plugin.
  5. `.claude-plugin/marketplace.json`: the two old entries become one, mirroring
     `plugin.json`.
  6. Add both old names to `RENAMED` in `tools/validate-plugins/checks/retired_names.py`,
     each mapped to `ceh-blog-and-seo`.
  7. Run `python tools/validate-plugins/validate.py` and edit every file it lists until it is
     green. A mention that states the present is edited, and a mention that states history
     stays and its file is added to `ALLOWED`.
- **Hooks and the validator** `hooks/hooks.json` and the three root scripts move unchanged with the base folder. In
  `tools/validate-plugins/checks/artifact_models.py`, `ceh-seo` leaves `READERS`, because its
  skills now sit in a plugin that carries the hooks, and the comment above the set is brought
  up to date. In `tools/validate-plugins/checks/hooks.py`, the fixtures that run
  `ceh-blog/artifact-render-hook.py` and `ceh-blog/generated-md-guard.py`, and the comment
  and message that name `ceh-blog`, take the new folder name. The three SEO skills bring no
  format the plugin's hooks do not already act on: `write-project-listing-text` carries the
  business plan and evidence models, which `draft-post` carries too.
- **Files that name the old plugins** Known today, and the check in step 7 finds any other: `CLAUDE.md` (tier table),
  `README.md` (Plugins and lifecycle tables), `docs/CATALOG.md`, `docs/CROSS_REFERENCES.md`
  (every registered path under either old folder), `docs/GETTING_STARTED.md`, `docs/IDEAS.md`,
  `docs/PLUGIN_DEPENDENCIES.md`, `docs/PLUGIN_VERSIONS.md` (two rows become one),
  `docs/STRATEGY.md` (the stage table and the Prove to Tell paragraph), `docs/VISION.md` (the
  Tell row), `.claude/rules/decision-artifact-validation.md`, the READMEs of `ceh-testing`
  and `ceh-usability-audit`, and two skill bodies in `ceh-usability-audit` that name a
  `ceh-seo` skill. Inside the plugin, every `ceh-blog:<skill>` and `ceh-seo:<skill>` name in a
  skill body or reference file takes the new prefix.
- **Version bumps in other plugins** Every other plugin whose files change gets a PATCH bump in `plugin.json` and
  `marketplace.json`, a row in the changelog's `### Plugin versions` table, and its row in
  `docs/PLUGIN_VERSIONS.md`. Known today: `ceh-testing` and `ceh-usability-audit`. A file
  registered in `docs/CROSS_REFERENCES.md` is edited in its canonical copy first and mirrored
  to every copy.
- **The vision's stage table** The PR replaces the two old names with `ceh-blog-and-seo` in the stage tables of
  `docs/VISION.md` and `docs/STRATEGY.md`. `decision-vision-governs.md` says a file and the
  vision that disagree are fixed in the same PR. Both plugins are in the Tell row, so no
  principle, goal or scope test changes, and the changelog entry says the table was edited
  and why.
- **The changelog entry** Under the PR's date: prose on the merge and its reason, the `### Plugin versions` table,
  and under `### Changed` the line for users: uninstall `ceh-blog` and `ceh-seo`, install
  `ceh-blog-and-seo`, and the six skills keep their names under the new prefix.

## Phases

### Phase 1: Merge into ceh-blog-and-seo

- **Builds:** "How the plugins are merged", steps 1 to 7, with "Hooks and the validator", "Files that
  name the old plugins", "Version bumps in other plugins", "The vision's stage table" and
  "The changelog entry". One PR.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, which
  includes the hook fixtures under the new folder name.
  `claude plugin validate plugins/standalone/ceh-blog-and-seo` passes.
  `ls plugins/standalone/ceh-blog-and-seo/skills` lists the six skills, and neither old
  folder exists. CI is green on the PR.
- **Status:** todo. Not covered by a command: loading the plugin in a fresh session with
  `claude --plugin-dir plugins/standalone/ceh-blog-and-seo` and seeing the six skills listed.
  The builder reports it as not run unless the user asks for it.

## Open

- May the merge PR edit the stage tables in `docs/VISION.md`, or does that need its own PR
  first?: It may, per "The vision's stage table".

## Record

- 2026-11-12 Planned: status ready

<!-- prettier-ignore-end -->
