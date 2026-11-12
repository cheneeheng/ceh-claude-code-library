---
schema: plan/v2
generated_from: merge-session-learning.yaml
generated_note: "Do not edit. artifact.py renders this file from merge-session-learning.yaml: edit the YAML, then run artifact.py render."
title: Merge ceh-session-diagnosis and ceh-session-to-skill into ceh-session-learning
status: built
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

The plugin audit of 2026-11-11 decided that `ceh-session-diagnosis` and `ceh-session-to-skill`
become one plugin, `ceh-session-learning`. Both read one session's transcript and turn it into
something durable: a fix when the session went wrong, a skill when it went right. This is the
smallest of the four merges, with no hooks, so it also proves the merge procedure the three
later plans repeat. It is for a user who installs one plugin to learn from a session. The flow
that matters most: with only `ceh-session-learning` installed, `/ceh-session-learning:diagnose-session`
dispatches `ceh-session-learning:transcript-analyst`, and
`/ceh-session-learning:turn-session-into-skill` runs beside it.

## Scope

**In:**

- One plugin, `ceh-session-learning`, holds the skills `diagnose-session` and
  `turn-session-into-skill` and the agent `transcript-analyst`, each working as before.
- `ceh-session-diagnosis` and `ceh-session-to-skill` no longer exist as plugins, in the
  marketplace or in any table or list that describes the live plugins.
- Every mention of either old name in a live file names `ceh-session-learning`, proven by the
  `retired-names` check.
- The changelog tells users to uninstall the two old plugins and install the new one.

**Out:**

- Any change to what the two skills or the agent do, including the audit's low findings.: A merge PR that only moves and renames stays reviewable as a rename. The findings are in
  `product/plans/plugin-audit-findings.yaml`.
- Rewording the three handoffs to `ceh-workflow-builder:build-agentic-workflow` in
  `turn-session-into-skill`.: They still resolve. They change when the workflow plugins move out of this repo.
- A copy of the old plugins under `archive/`.: Their content lives on in the new plugin, so a copy would be a second source.
- Rewriting the old names inside `product/`, `audits/`, `archive/` and `CHANGELOG.md`.: Those files are records of what was true when they were written.

## Design

- **Depends on** Phase 1 of `product/plans/retired-names-check-and-archives.yaml`, the `retired-names` check,
  is merged before this plan is built.
- **How the plugins are merged** The base is `ceh-session-diagnosis`, because it holds the agent.

  1. `git mv plugins/standalone/ceh-session-diagnosis plugins/standalone/ceh-session-learning`.
  2. `git mv plugins/standalone/ceh-session-to-skill/skills/turn-session-into-skill
     plugins/standalone/ceh-session-learning/skills/`.
  3. Fold what `ceh-session-to-skill/README.md` says into the new README, which gets one
     table of both skills and the agent, then `git rm -r plugins/standalone/ceh-session-to-skill`.
  4. `plugin.json`: `name` becomes `ceh-session-learning`, `description` covers both uses in
     one sentence, `keywords` are the union, and `version` is the next MAJOR of the base
     plugin's version at build time (`2.0.0` from `1.0.x`), per `decision-version-levels.md`.
     The base's `tuning.json` moves with the folder and the other is deleted with its plugin.
  5. `.claude-plugin/marketplace.json`: the two old entries become one, mirroring
     `plugin.json`.
  6. Add both old names to `RENAMED` in `tools/validate-plugins/checks/retired_names.py`,
     each mapped to `ceh-session-learning`.
  7. Run `python tools/validate-plugins/validate.py` and edit every file it lists until it is
     green. A mention that states the present is edited, and a mention that states history
     stays and its file is added to `ALLOWED`.
- **Files that name the old plugins** Known today, and the check in step 7 finds any other: `CLAUDE.md` (tier table),
  `README.md` (Plugins and lifecycle tables), `docs/CATALOG.md`, `docs/CROSS_REFERENCES.md`,
  `docs/GETTING_STARTED.md`, `docs/IDEAS.md`, `docs/PLUGIN_VERSIONS.md` (two rows become
  one), `docs/RETRO_WORKFLOW.md`, `docs/STRATEGY.md`, `docs/VISION.md` (the Every step row),
  and `plugins/standalone/ceh-every-session/skills/prevent-repeat-mistake/SKILL.md`, which
  names `diagnose-session` by its full name. Inside the plugin, `diagnose-session` step 3
  names the agent by its full name, which becomes `ceh-session-learning:transcript-analyst`.
- **Version bumps in other plugins** Every other plugin whose files change gets a PATCH bump in `plugin.json` and
  `marketplace.json`, a row in the changelog's `### Plugin versions` table, and its row in
  `docs/PLUGIN_VERSIONS.md`. Known today: `ceh-every-session`. A file registered in
  `docs/CROSS_REFERENCES.md` is edited in its canonical copy first and mirrored to every copy.
- **The vision's stage table** The PR replaces the two old names with `ceh-session-learning` in the stage tables of
  `docs/VISION.md` and `docs/STRATEGY.md`. `decision-vision-governs.md` says a file and the
  vision that disagree are fixed in the same PR. Both plugins are in the Every step row, so
  no principle, goal or scope test changes, and the changelog entry says the table was
  edited and why.
- **The changelog entry** Under the PR's date: prose on the merge and its reason, the `### Plugin versions` table,
  and under `### Changed` the line for users: uninstall `ceh-session-diagnosis` and
  `ceh-session-to-skill`, install `ceh-session-learning`, and the two skills and the agent
  keep their names under the new prefix.

## Phases

### Phase 1: Merge into ceh-session-learning

- **Builds:** "How the plugins are merged", steps 1 to 7, with "Files that name the old plugins",
  "Version bumps in other plugins", "The vision's stage table" and "The changelog entry".
  One PR.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
  `claude plugin validate plugins/standalone/ceh-session-learning` passes.
  `ls plugins/standalone/ceh-session-learning/skills` lists `diagnose-session` and
  `turn-session-into-skill`, `ls plugins/standalone/ceh-session-learning/agents` lists
  `transcript-analyst.md`, and neither old folder exists. CI is green on the PR.
- **Status:** done, Commit dcd8adb. `python tools/validate-plugins/validate.py` printed
  `OK: all plugin checks passed`. `claude plugin validate plugins/standalone/ceh-session-learning`
  printed `Validation passed`. `skills/` lists `diagnose-session` and `turn-session-into-skill`,
  `agents/` lists `transcript-analyst.md`, and neither old folder exists. CI run 43202288693 on
  PR #262 succeeded. Not covered by a command: loading the plugin in a fresh session with
  `claude --plugin-dir plugins/standalone/ceh-session-learning` and seeing both skills and the
  agent listed. The builder reports it as not run unless the user asks for it.

## Open

- Does the merged plugin start at `1.0.0` as a new plugin, or continue the base plugin's
  version with a MAJOR bump?: It continues with a MAJOR bump, because `decision-version-levels.md` names a rename as a
  MAJOR change. The three later merge plans take the same answer.
- May the merge PR edit the stage tables in `docs/VISION.md`, or does that need its own PR
  first?: It may, per "The vision's stage table".

## Record

- 2026-11-12 Planned: status ready
- 2026-11-12 PR: #258 https://github.com/cheneeheng/ceh-claude-code-library/pull/258
- 2026-11-12 Built Phase 1: `ceh-session-diagnosis` and `ceh-session-to-skill` merged into `ceh-session-learning` 2.0.0,
  with both old names in `RENAMED` and `ceh-every-session` bumped. Built in one PR with the
  three other merge plans, at the user's request.
- 2026-11-12 PR: #262 https://github.com/cheneeheng/ceh-claude-code-library/pull/262

<!-- prettier-ignore-end -->
