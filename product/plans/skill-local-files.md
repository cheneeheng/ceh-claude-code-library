---
schema: plan/v2
generated_from: skill-local-files.yaml
generated_note: "Do not edit. artifact.py renders this file from skill-local-files.yaml: edit the YAML, then run artifact.py render."
title: Every file a skill needs lives in the skill's own folder, and copies are checked byte for byte
status: building
created: 2026-11-07
---

<!-- prettier-ignore-start -->

## Goal

Every file a skill reads, copies or runs (its templates, schemas, models, reference files and
scripts) sits inside that skill's folder, so a skill folder works on its own wherever it is
copied, `tools/skills-sync` included. A file several skills need is copied into each, and one
`validate.py` check keeps every copy byte-identical: two bundled files at the same path inside
their skill folders must match. A plugin's root keeps only what hooks and agents run, in
`scripts/`. This lands before Phase 6 of `product/plans/artifact-validation.md`, so the formats
it adds start in the new layout.

## Scope

**In:**

- One `copies` check in `validate.py`: every file under `assets/`, `references/` or `scripts/`
  at the same path relative to its skill folder (`references/plan-schema.md`,
  `scripts/artifact.py`) is byte-identical across every skill of every plugin, and each
  plugin-level artifact script joins the group of its `scripts/<name>` path. It replaces the
  identity parts of `checks/templates.py` and `checks/artifact_models.py`, and its error names
  every copy.
- The three plan plugins (`ceh-build-planning`, `ceh-build-from-plan`,
  `ceh-check-build-against-plan`) carry the `plan` format and `artifact.py` inside each plan
  skill, and those skills run `${CLAUDE_SKILL_DIR}/scripts/artifact.py`.
- Every other plugin-level `assets/` and `references/` file, and every plugin-level script a
  skill runs, moves into each skill that cites it, and each citation becomes skill-relative,
  in SKILL.md files and in reference files alike.
- A layout check: a plugin root with an `assets/` or `references/` folder, a skill or agent
  citing `${CLAUDE_PLUGIN_ROOT}/assets/` or `${CLAUDE_PLUGIN_ROOT}/references/`, or a reference
  file under a skill naming `${CLAUDE_PLUGIN_ROOT}` or `<plugin root>` at all, fails
  `validate.py`. Scripts in skill folders are compiled and shellchecked like plugin-level ones.
- The rules, docs and checklists say the new layout: `decision-skill-bundled-files.md`,
  `decision-output-templates.md`, `decision-artifact-validation.md`, `plugins/CLAUDE.md`, the
  add-plugin-component `SKILL.md` and `SKILL.template.md`, `tools/validate-plugins/README.md`,
  every plugin README or plugin doc naming a moved path, and `docs/CROSS_REFERENCES.md` with
  every whole-file copy still registered, at its new path, including the copies the moves
  create.

**Out:**

- Plugin-level scripts that only hooks or agents run: Hooks and agents have no skill folder, and `hooks.json` wires its scripts through
  `${CLAUDE_PLUGIN_ROOT}`. The agent test runners in `ceh-python-service` and
  `ceh-web-frontend`, and every hook script, stay in the plugin's `scripts/`.
- Changing `docs/VISION.md` principle 6 or `docs/STRATEGY.md` handoff rule 2: The user kept both as written on 2026-11-07: a copied standard is copied and registered,
  and the `copies` check adds to the registry rather than replacing it.
- A sync script that copies one file over its copies: The user chose the check alone. Its error names every copy, and fixing means copying the
  edited file over the others.
- Phase 6 of `artifact-validation.md` (the remaining YAML formats): Its own plan, after this one, once the user gives the trial verdict.
- Content blocks copied inside a SKILL.md, README or agent: No byte check can cover part of a file, so they stay registered in
  `docs/CROSS_REFERENCES.md` as before.
- The repo-local skills in `.claude/skills/`: They already keep their `assets/`, `references/` and `scripts/` in the skill folder.
- Eval cases under `evals/`: They never cite bundled file paths, and running them costs model calls.

## Design

- **What groups as a copy:** Only files under a skill's `assets/`, `references/` or `scripts/` take part, so `SKILL.md`
  and `evals/` are never grouped. The key is the file's path relative to the skill folder that
  holds it, `plugins/standalone/<plugin>/skills/<skill>/`, never the bare filename. So
  `references/meridian/brand.css` and `references/tidewater/brand.css` stay distinct, as do the
  two `main.py` scaffolds in `ceh-ag-ui`. `__pycache__` is skipped. The review of 2026-11-07
  hashed the tree keyed this way: all 16 groups are byte-identical today.

  Until Phase 3 empties them, a plugin root's `assets/` and `references/` count as an owner
  folder too, so `ceh-build-planning/references/plan-schema.md` groups with the skill copies,
  and the plugin-level copies shared by `ceh-workflow-builder` and `ceh-workflow-runner` stay
  checked, as `checks/templates.py` checks them today.

  The plugin-level `scripts/artifact.py`, `scripts/artifact-render-hook.py` and
  `scripts/generated-md-guard.py` join the `scripts/<name>` group, so the hook's copy of
  `artifact.py` matches the skills' copies, and the two hook scripts match across plugins as
  `checks/artifact_models.py` checks today. No other plugin-level script joins a group, because
  `skill-started-guard.py` and the agent test runners differ between plugins on purpose.
- **Where the check lives:** `tools/validate-plugins/checks/copies.py`, run by `validate.py` like every other module,
  with a `check()` that calls `fail(<copy path>, "differs from its copy <first path>; copies:
  <every path>")` per differing file. From `checks/templates.py`, lines 83 to 87 (the
  `by_name` identity loop), the `by_name.append` calls at lines 69 and 81, and the identity
  sentence of its docstring go. From `checks/artifact_models.py`, the identity loop at lines
  32 to 43 and its docstring sentence go. `artifact_models.py` keeps its other jobs: a model
  beside its schema with `../assets/<name>.template.yaml`, each plugin carrying a model also
  carrying the plugin-level artifact scripts, and the uv template comparison. The validator
  README gets a `copies` row, and its rows at lines 42 to 43 drop the identity wording.
- **The layout check:** Added to `checks/copies.py`, since it guards the same layout. It fails a plugin root holding
  an `assets/` or `references/` folder; a SKILL.md or agent naming
  `${CLAUDE_PLUGIN_ROOT}/assets/` or `${CLAUDE_PLUGIN_ROOT}/references/`; and a reference file
  under `skills/*/references/` naming `${CLAUDE_PLUGIN_ROOT}` or `<plugin root>`, because a
  copied reference file can only point inside its own skill. `checks/scripts.py` line 25 also
  globs `skills/*/scripts/*`, so moved scripts are still compiled and shellchecked. The layout
  part lands in Phase 3, once nothing violates it.
- **What moves where:** Each file goes into every skill whose SKILL.md, or whose reference files, cite it.
  A template and its schema always travel as a pair, because `checks/templates.py` requires a
  template's schema in the sibling `references/` and the schema cites `../assets/`. From the
  inventory of 2026-11-07, confirmed by the review:

  - `ceh-build-planning`: `plan.template.md`, `plan.template.yaml`, `plan-schema.md`,
    `plan-model.py` into `write-build-plan` and `review-build-plan`.
  - The three plan plugins: `scripts/artifact.py` copied into each plan skill's `scripts/`
    (`write-build-plan`, `review-build-plan`, `implement-from-plan`,
    `check-build-against-plan`). The plugin copy stays for the render hook.
  - `ceh-blog`: `ask-the-author.md` into `draft-post`, `edit-post`, `repurpose-post`, and each
    format pair into the skills citing its schema.
  - `ceh-business-plan`: `business-plan-schema.md` with its template into all nine skills
    citing it; `build-plan-html.cjs`, `business-plan-page.html` and `brand.css` into
    `develop-business-plan` (`scripts/` and `assets/`), whose script reads `../assets/`
    relative to itself (`build-plan-html.cjs` line 10).
  - `ceh-competitor-analysis`: `report-page.html` into both skills.
  - `ceh-documentation`: `docs-standard.md` into its four citing skills.
  - `ceh-usability-audit`: `personas-and-severity.md` into `audit-interface` and
    `simulate-newcomer-first-run`.
  - `ceh-orchestration-lab`: `run-log.md`, both format pairs, `token_usage.py` and
    `dispatch_ledger.py` into `orchestrate` and `plan-then-implement`.
  - `ceh-workflow-builder` and `ceh-workflow-runner`: `flow-config-schema.md` and the
    `approval` and `run-state` pairs into `build-agentic-workflow` and `run-agentic-workflow`,
    and `build-agentic-workflow/references/emitted-templates.md` line 69 cites
    `../references/flow-config-schema.md`.
  - `ceh-git-workflow`: `check-semver.py` into `update-changelog/scripts/`;
    `assets/union.attributes` into `scripts/` beside `sync-agents-workspace.py`, the hook
    script that reads it, with its path constant at line 34 updated.
- **How citations change:** A SKILL.md cites a file to read as `references/<file>` or `assets/<file>`, resolved from the
  skill folder as `checks/references.py` does today, and a script to run as
  `${CLAUDE_SKILL_DIR}/scripts/<file>`, in the body and in `allowed-tools` alike
  (`add-plugin-component/SKILL.md` line 133 says Claude Code substitutes it in both). So
  `update-changelog` pre-approves `Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check-semver.py *)`.

  A reference file keeps citing siblings as `../assets/` or `../references/`. Claude Code does
  not substitute `${CLAUDE_SKILL_DIR}` in reference files, so a reference file that runs a
  script names it as `<skill folder>/scripts/<file>`, and the SKILL.md that loads it states
  `the skill folder is ${CLAUDE_SKILL_DIR}`, as `orchestrate` and `plan-then-implement` state
  the plugin root today (`orchestrate/SKILL.md` line 18). This covers `run-log.md` lines 49 and
  51. A copied schema that names something only one skill holds names that skill in prose,
  never by a path: the business-plan schema says `develop-business-plan` renders the page with
  its own script and `brand.css`, and only `develop-business-plan/SKILL.md` gives the
  `node ${CLAUDE_SKILL_DIR}/scripts/build-plan-html.cjs` command.
- **artifact.py inside a skill:** No code change. It finds models with `PLUGIN_ROOT.glob("**/references/<name>-model.py")`
  (line 41), where `PLUGIN_ROOT` is two levels above the script (line 28): the plugin root for
  the hook's copy, the skill folder for a skill's copy. Both find the skill-local
  `plan-model.py`, as do the render hook (line 30) and `model_vs_template.py`.
  `plan-schema.md` says the CLI is `scripts/artifact.py` in the skill, beside the
  `references/` that holds the model.
- **CROSS_REFERENCES.md:** Every entry stays, and the `copies` check runs in addition to the registry, as VISION
  principle 6 and STRATEGY handoff rule 2 require ("copied ... and registered"). Each entry's
  canonical path and copy rows are updated where a file moved (lines 335, 402 to 407, 545, 590,
  601 and 602 among them). The copies the moves create get rows too, per
  `decision-shared-standards-duplication.md` ("Register every duplicated block"): within one
  plugin, the entry's canonical file is the copy in the skill that writes the format, or the
  first skill citing it in alphabetical order when none writes it, and the other skills' copies
  are its rows. A new entry is added for each moved file that had no entry: `ask-the-author.md`
  and the three blog format pairs, the business-plan format pair, `report-page.html`,
  `docs-standard.md`, `run-log.md` with the two run format pairs and the two orchestration-lab
  scripts, and `artifact.py`. The intro gains one line: a whole bundled-file copy is also
  checked byte for byte by `copies`.
- **Versions and changelog:** PATCH for every plugin a phase touches, in that phase's PR, per
  `decision-version-levels.md`. Every phase's PR, Phase 1 included, adds its `CHANGELOG.md`
  entry under the PR's date per `decision-changelog-sections.md`, and the `docs/PLUGIN_VERSIONS.md`
  rows of any plugin it bumps. Phase 1 changes only `tools/` and bumps nothing.

## Phases

### Phase 1: The copies check

- **Builds:** `checks/copies.py` with the grouping in Design, What groups as a copy, the removals in
  Design, Where the check lives, `checks/scripts.py` covering `skills/*/scripts/*`, the
  validator README rows, and a changelog entry.
- **Check:** `python tools/validate-plugins/validate.py` exits 0. Then change one byte of
  `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/references/plan-schema.md`,
  rerun: it exits 1 with a `copies` error naming that file and its two other copies, in
  `ceh-build-planning/references/` and `ceh-build-from-plan/skills/implement-from-plan/references/`.
  Revert.
- **Status:** done, `python tools/validate-plugins/validate.py`: "OK: all plugin checks passed"; with one byte
  appended to the check-build-against-plan copy, `[copies]` failed naming it and the other two
  copies; reverted, OK again.

### Phase 2: The plan plugins in the new layout

- **Builds:** The `ceh-build-planning` and plan-skill moves from Design, What moves where, the SKILL.md
  citations of the four plan skills changed to `${CLAUDE_SKILL_DIR}/scripts/artifact.py` and
  skill-local `assets/` and `references/`, `plan-schema.md` updated in all copies, the plan
  plugins' READMEs, and the Build plan format entry of `docs/CROSS_REFERENCES.md` at the new paths with a row for each
  new copy, plus a new `artifact.py` entry. PATCH bumps
  for the three plan plugins.
- **Check:** `python tools/validate-plugins/validate.py` exits 0, and
  `uv run --script <path>/scripts/artifact.py check product/plans/skill-local-files.yaml`
  exits 0 for each of these four paths under `plugins/standalone/`:
  `ceh-build-planning/skills/write-build-plan`, `ceh-build-planning/skills/review-build-plan`,
  `ceh-build-from-plan/skills/implement-from-plan`, and
  `ceh-check-build-against-plan/skills/check-build-against-plan`.
- **Status:** todo

### Phase 3: Every other plugin, the layout check, and the rules

- **Builds:** The remaining moves from Design, What moves where, with their citations per Design, How
  citations change; the layout check; the rules, docs, READMEs and checklists named in Scope
  In; the remaining `docs/CROSS_REFERENCES.md` updates per Design. PATCH bumps for every
  plugin touched.
- **Check:** `python tools/validate-plugins/validate.py` exits 0;
  `grep -rnE 'CLAUDE_PLUGIN_ROOT\}/(assets|references)|<plugin root>' plugins` prints nothing;
  and `grep -rn 'CLAUDE_PLUGIN_ROOT}/scripts' plugins --include=SKILL.md` lists only hook or
  agent scripts. Then create `plugins/standalone/ceh-blog/references/x.md` and rerun
  `validate.py`: it exits 1 with a layout error naming that folder. Delete it.
- **Status:** todo

## Open

None

## Record

- 2026-11-07 Planned: status ready
- 2026-11-07 Reviewed: Revise first, 5 blocking (copies key groups every SKILL.md and evals file; Build plan format
  and Usability persona entries hold non-whole-file copies; run-log.md and
  business-plan-schema.md script citations escape every check; decision-shared-standards-duplication
  and add-plugin-component SKILL.md missing from In; VISION and STRATEGY still require
  registration)
- 2026-11-07 PR: #211 https://github.com/cheneeheng/ceh-claude-code-library/pull/211
- 2026-11-07 Built Phase 1: validate.py OK, and red on a one-byte change naming all three plan-schema.md copies
- 2026-11-07 PR: #213 https://github.com/cheneeheng/ceh-claude-code-library/pull/213

<!-- prettier-ignore-end -->
