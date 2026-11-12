---
schema: plan/v2
generated_from: retired-names-check-and-archives.yaml
generated_note: "Do not edit. artifact.py renders this file from retired-names-check-and-archives.yaml: edit the YAML, then run artifact.py render."
title: A validator check for retired plugin names, then two plugins archived
status: building
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

The plugin audit of 2026-11-11 ended with 27 plugins becoming 21: two archived and four merges.
`validate.py` resolves a `ceh-<plugin>:<skill>` name only while its plugin still exists, and never
a plugin named on its own, so a removed or renamed plugin leaves stale names behind that no check
sees. This plan adds the check first, then archives `ceh-orchestration-lab` and
`ceh-git-datastore` with it in place, for the maintainer of this repo and the agents that land
the four merge plans after it. The flow that matters most: a PR moves a plugin to `archive/`, a
skill body elsewhere still names it, and `validate.py` fails with the file and line.

## Scope

**In:**

- `validate.py` fails, with file and line, on any mention of a retired plugin name outside the
  exempt paths: a name with a folder under `archive/` and no live plugin, or a name listed as
  renamed. This covers the bare name and the `ceh-<plugin>:<skill>` form.
- A mention that states history on purpose passes when its file is listed for that name, as
  `.claude/rules/decision-evaluation.md` is for `ceh-evaluation`.
- `ceh-orchestration-lab` is in `archive/`, gone from the marketplace and from every table and
  list that describes the live plugins, with `ceh-every-session:whats-next` no longer naming
  its two skills.
- `ceh-git-datastore` is in `archive/` whole, gone from the marketplace and from every table
  and list that describes the live plugins, and recorded in `archive/README.md` as archived
  unused, not rejected.

**Out:**

- Fixing the low findings of the two archived plugins.: The audit decided they need no fix until a plugin is re-enabled.
- Moving orchestration lessons into `ceh-coding-conduct:agent-coding-contract`.: Decided on 2026-11-11: archive and drop the lessons.
- The experiment's run folders in each project's `.agents_workspace/orchestration-lab/`.: The user archives the runs themselves, so the PR leaves them alone.
- The words "orchestration-lab runs" in `.claude/rules/decision-artifact-locations.md` and
  `docs/STRATEGY.md`.: They say where existing run folders sit, which stays true after the archive. They hold no
  plugin name, so the check passes them.
- A check for unknown `ceh-` tokens of any kind.: Nineteen such tokens exist that are not plugins, such as `ceh-claude-code-library` and
  `ceh-ws`, so that check would need a longer allowlist than the one it replaces.
- Rewriting plugin names inside `product/`, `audits/`, `archive/` and `CHANGELOG.md`.: Those files are records of what was true when they were written.

## Design

- **The check: `tools/validate-plugins/checks/retired_names.py`** One new module with a `check()` function, one line in `CHECKS` in `validate.py` after
  `skill_refs`, and a `retired-names` row in `tools/validate-plugins/README.md`, as that README
  asks of every new check. Stdlib only. It holds two constants:

  - `RENAMED: dict[str, str]`, old plugin name to the plugin that replaced it. Empty in this
    plan. Each merge plan adds its old names in its own PR.
  - `ALLOWED: dict[str, set[str]]`, retired name to the repo-relative files that may still
    name it.

  The retired names are every `archive/ceh-*` folder name with no folder of the same name
  under `plugins/standalone/`, plus the keys of `RENAMED`. The live test matters because
  `archive/ceh-git-workflow/` holds one retired skill of a plugin that is still live.

  The check reads the files the `hygiene` check walks (root `*.md`, and text files under
  `plugins/`, `docs/`, `tools/`, `.claude/`, `.github/`, `examples/`), plus
  `.claude-plugin/marketplace.json`, and skips `product/`, `audits/`, `archive/`,
  `CHANGELOG.md` and its own file. It gets the file list from `committable_files()` in
  `checks/hygiene.py`, which already returns tracked and new files git does not ignore, and
  filters it by `HYGIENE_ROOTS` as that check does. In each line it finds every token matching
  `\bceh-[a-z0-9]+(?:-[a-z0-9]+)*` and fails when the whole token is a retired name and the
  file is not in `ALLOWED` for it: `<file>:<line>: retired plugin name '<name>' (<replaced by
  or archived>)`. Matching the whole token keeps `ceh-blog-and-seo` from tripping on
  `ceh-blog`.
- **Mentions that exist today** Four archived names are mentioned outside `archive/` today, each as history, so each goes
  into `ALLOWED` with its files: `ceh-evaluation` (`.claude/rules/decision-evaluation.md`,
  `.claude/skills/evaluate-plugin/SKILL.md`), `ceh-ops` and `ceh-scaffolding`
  (`docs/CROSS_REFERENCES.md`), and `ceh-plan-build-review` (`docs/IDEAS.md`). The rule for
  every later mention, here and in the merge plans: a mention that states the present is
  edited, and a mention that states history stays and its file is added to `ALLOWED`.
- **How a plugin is archived** `git mv plugins/standalone/<plugin> archive/<plugin>`, whole, so re-enabling is a move back.
  The folder under `archive/` makes the name retired with no edit to the check. The same PR:

  - removes the plugin's entry from `.claude-plugin/marketplace.json` and its row from
    `docs/PLUGIN_VERSIONS.md`;
  - removes it from the tier table in `CLAUDE.md`, the Plugins and lifecycle tables in
    `README.md`, its group in `docs/CATALOG.md`, its entries in `docs/GETTING_STARTED.md`,
    `docs/CROSS_REFERENCES.md`, `docs/ENVIRONMENT_VARIABLES.md` and
    `docs/PLUGIN_DEPENDENCIES.md`, and the stage tables in `docs/VISION.md` and
    `docs/STRATEGY.md`;
  - adds a dated section to `archive/README.md` with the reason;
  - lowers `MAX_TOTAL_DESCRIPTION_LEN` in `checks/budget.py` to the new total, as that check's
    ratchet asks;
  - adds the `CHANGELOG.md` entry under the PR's date, with a line telling users to uninstall
    the plugin, and PATCH bumps for every other plugin whose files changed.

  A removed plugin has no manifest left to bump, so the MAJOR change of
  `decision-version-levels.md` is its removal from the marketplace.
- **The vision's stage table in the archive PRs** Each archive PR edits the stage table in `docs/VISION.md`, and the orchestration-lab PR also
  removes the paragraph below it about the experiment. `decision-vision-governs.md` says a file
  and the vision that disagree are fixed in the same PR, and the vision itself says the plugin
  "moves to `archive/`" when the experiment ends. No principle, goal or scope test changes.
  The changelog entry says the vision's table was edited and why.
- **What else names `ceh-orchestration-lab`** Beyond the lists above: the two rows in the User-only skills table of
  `plugins/standalone/ceh-every-session/skills/whats-next/SKILL.md`, which `repo_rules`
  checks (a PATCH bump of `ceh-every-session`), `plugins/CLAUDE.md`, which names its two
  skills as user-only examples, the `CLAUDE_CODE_SUBAGENT_MODEL` row in
  `docs/ENVIRONMENT_VARIABLES.md`, and `docs/IDEAS.md`. The archive section reads: the
  experiment ended on 2026-11-11, its lessons were dropped by decision, and its run folders
  stay in each project's workspace.
- **What else names `ceh-git-datastore`** Beyond the lists above: the allowed scaffold and script bundles in `plugins/CLAUDE.md` and
  `.claude/rules/decision-skill-bundled-files.md`, and its README row in
  `docs/PLUGIN_DEPENDENCIES.md`. The archive section reads: archived unused on 2026-11-11, not
  rejected, and moving the folder back under `plugins/standalone/` re-enables it.
- **The check in its own PR, both archives in one** The check merges first, so the archive PR runs against it in CI. A green run on the archive
  PR then shows the check finding nothing left, which a single PR for all three could not
  show. Both archives share one PR, at the user's request on 2026-11-12.

## Phases

### Phase 1: The retired-names check

- **Builds:** `checks/retired_names.py` with `RENAMED` empty and `ALLOWED` holding the four names under
  "Mentions that exist today", its line in `CHECKS`, and its README row. No plugin changes, so
  no version bump. The PR carries its `CHANGELOG.md` entry.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`. Then the
  negative probe: write `docs/_probe.md` holding the line `see ceh-advisor`, run
  `python tools/validate-plugins/checks/retired_names.py`, and it exits 1 naming
  `docs/_probe.md:1` and `ceh-advisor`. Delete the file, run it again, and it exits 0.
- **Status:** done, `python tools/validate-plugins/validate.py` printed `OK: all plugin checks passed`. With the
  probe, `retired_names.py` exited 1 with
  `docs/_probe.md:1: retired plugin name 'ceh-advisor' (archived)`, and 0 once it was deleted.

### Phase 2: Archive ceh-orchestration-lab

- **Builds:** "How a plugin is archived" applied to `ceh-orchestration-lab`, with "The vision's stage
  table in the archive PRs" and "What else names `ceh-orchestration-lab`".
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, with the
  folder at `archive/ceh-orchestration-lab/` and absent from `plugins/standalone/`.
  `claude plugin validate plugins/standalone/ceh-every-session` passes. CI is green on the PR.
- **Status:** todo

### Phase 3: Archive ceh-git-datastore

- **Builds:** "How a plugin is archived" applied to `ceh-git-datastore`, with "The vision's stage table in
  the archive PRs" and "What else names `ceh-git-datastore`".
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, with the
  folder at `archive/ceh-git-datastore/` and absent from `plugins/standalone/`, and
  `ls plugins/standalone` lists 25 plugins. CI is green on the PR.
- **Status:** todo

## Open

- May the archive PRs edit the stage table in `docs/VISION.md`, or does that need its own PR
  first?: They may, per "The vision's stage table in the archive PRs". The audit called one PR
  defensible, and the changelog entry says so.

## Record

- 2026-11-12 Planned: status ready
- 2026-11-12 PR: #258 https://github.com/cheneeheng/ceh-claude-code-library/pull/258
- 2026-11-12 Built Phase 1: `checks/retired_names.py`, its line in `CHECKS`, and its README row. The negative probe
  failed on `ceh-advisor` and passed once deleted.
- 2026-11-12 PR: #260 https://github.com/cheneeheng/ceh-claude-code-library/pull/260
- 2026-11-12 Design changed: "One PR per phase: The check merges first, so each archive PR runs against it in CI. A green
  run on an archive PR then shows the check finding nothing left, which a single PR for all
  three could not show." became one PR for the check and one for both archives, because the
  user asked in the session for phases 2 and 3 in a single PR.

<!-- prettier-ignore-end -->
