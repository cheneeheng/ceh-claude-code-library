---
schema: plan/v2
generated_from: move-product-to-workspace.yaml
generated_note: "Do not edit. artifact.py renders this file from move-product-to-workspace.yaml: edit the YAML, then run artifact.py render."
title: This repo's own product artifacts move from root product/ to .agents_workspace/product/
status: ready
created: 2026-11-15
---

<!-- prettier-ignore-start -->

## Goal

`decision-artifact-locations.md` puts every product artifact in `.agents_workspace/product/`,
and lets this repo keep its root `product/` only "until a plan moves it". This is that plan.
After it, the 106 files git tracks under `product/` (`ARCHITECTURE.yaml` and its `.md`, 82
plan files, 7 fix records, 15 retro files) live at the same sub-paths under
`.agents_workspace/product/`, committed in the agents workspace repo, and the source repo
tracks no `product/` folder. Every committed rule, doc and tool that cites a root `product/`
file of this repo names its new path, so a session that follows a rule's `source:` or a code
comment finds the file. The flow that matters most: a session in this repo writes or reads a
plan, a fix record or a retro through the skills' default path, with no exception in
`CLAUDE.md`.

## Scope

**In:**

- Every file git tracks under `product/` sits at the same sub-path under
  `.agents_workspace/product/`, committed in the agents workspace repo, and `git ls-files
  product` in the source repo prints nothing.
- `tools/validate-plugins/checks/artifact_models.py` checks each
  `.agents_workspace/product/plans/*.yaml` against its model and its rendered Markdown when
  that folder exists, and skips the step when it does not, as in CI.
- `tools/validate-plugins/checks/hygiene.py` no longer scans `product`, and its README row,
  `decision-no-home-paths.md` and `docs/RETRO_WORKFLOW.md` stop naming this repo's
  `product/` as a scanned root.
- Every committed reference to one of this repo's root `product/` files names its
  `.agents_workspace/product/` path: the `source:` lines and body of the rules in
  `.claude/rules/`, the comments and docstring of `artifact_models.py`, the comments in
  `artifact_paths.py` and `hooks.py` that cite `markdown-formats-yaml.yaml`, the
  `tools/validate-plugins/README.md` `artifact-models` and `retired-names` rows, and
  `docs/IDEAS.md`.
- Root `CLAUDE.md` names no `product/` location: its Structure block drops the `product/`
  line and lists `product/` under `.agents_workspace/`. `decision-artifact-locations.md`
  drops "this repo keeps its own `product/` until a plan moves it", and `docs/STRATEGY.md`
  drops the matching "Where the repo does not match yet" line, leaving that section's intro
  followed by `None.`
- `.agents_workspace/BACKLOG.md`'s Source convention no longer says a path starting
  `product/` is in the repo, and a `CHANGELOG.md` entry records the move.

**Out:**

- CI checking this repo's plans: `.agents_workspace/` is git-ignored and pushed to a private remote, so the CI checkout
  has no plans to check. The render hook checks each plan when Claude Code edits it, and
  the local `validate.py` run still checks every plan. A CI job in the agents workspace
  repo can be added if a stale plan ever reaches a commit.
- Editing the text of the moved files: A built plan stays as written, and retired names already treats `product/` as a record
  of what was true when written. Paths inside the moved plans, fixes and retros that name
  root `product/` are left as history.
- Moving `docs/VISION.md` and `docs/STRATEGY.md`: They are maintainer docs this repo's `CLAUDE.md` and `decision-vision-governs.md` cite
  at `docs/`, and moving them is a separate decision.
- Rewriting history to remove `product/` from past commits: The files were public by choice, and a history rewrite breaks every clone.
- The generic `product/` patterns in `checks/hooks.py`, `checks/artifact_paths.py`, `checks/templates.py` and the `fix-record-model.py` copies: They describe a target project's paths, or the old path a plugin must reject, not this
  repo's folder. The three comments in those files that cite this repo's
  `markdown-formats-yaml.yaml` are In.
- CHANGELOG entries and audit reports that name `product/`: They record what was true on their date.

## Design

- **Order of the move:** Copy first, commit in the agents workspace repo, then `git rm -r product` in the source
  repo, so no step leaves a file in neither repo. The copy merges into the existing
  `.agents_workspace/product/retros/`, whose only file (`2026-11-11-session-4aeb72cf.md`)
  shares no name with `product/retros/`, checked by `ls` on 2026-11-15. The tracked
  `product/retros/2026-10-18-claude-code-command-center-repeat-mistake/` folder (three
  `.py` files) moves with the rest. This plan's own two files are tracked once the plan's
  PR merges, so they move too. In the workspace repo, on whatever branch it is on, the
  commit stages `product/` only (`git -C .agents_workspace add product`), so an unrelated
  modified file stays out, and its message is `chore(workspace): move product artifacts
  from the source repo`. Then `git rm -r product` runs, and any untracked file still under `product/` is
  moved by hand, so no `product/` folder is left on disk.
- **The plan check without CI:** The loop at `artifact_models.py` line 150 reads
  `REPO / ".agents_workspace" / "product" / "plans"`. A missing folder yields no files from
  `glob`, so CI passes with no extra branch. `validate.py` run locally checks every plan,
  which is the gate `decision-pr-review.md` names.
- **References that change:**
  - `.claude/rules/decision-artifact-locations.md`, `decision-artifact-validation.md`,
    `decision-business-plan-readers.md`, `decision-pr-review.md`,
    `decision-skill-bundled-files.md`: each `product/...` path of this repo gets the
    `.agents_workspace/` prefix.
  - `decision-no-home-paths.md`: `product/` leaves the list of scanned roots, and the Why
    keeps its history ("while `product/` sat outside the check") as written.
  - `docs/RETRO_WORKFLOW.md` line 75: the sentence on this repo's `product/` goes.
  - `docs/IDEAS.md` line 174: the retro path gets the `.agents_workspace/` prefix.
  - `tools/validate-plugins/README.md`: `product/` leaves the `hygiene` row and the list of
    skipped record folders in the `retired-names` row, and the `artifact-models` row names
    the new plans folder and that CI skips it.
  - `checks/artifact_paths.py` lines 6 and 36 and `checks/hooks.py` line 925: the
    `product/plans/markdown-formats-yaml.yaml` citation gets the `.agents_workspace/` prefix.
  - `artifact_models.py` docstring line 4 and the comments at lines 24 to 28 and 38.
  - `checks/retired_names.py` line 33 comment: `product/` leaves the list of record folders.
- **Memory and skills:** No skill changes: once root `CLAUDE.md` names no location, every skill uses
  `.agents_workspace/product/`, which the consolidate plan already made the default. The
  user's auto-memory that names `product/plans/setup-script.yaml` is updated by the session
  that builds this plan, because it lives outside the repo.

## Phases

### Phase 1: Move the files and point the validator at them

- **Builds:** The copy, the workspace commit and `git rm -r product` per "Order of the move". The
  `artifact_models.py` loop path per "The plan check without CI". `product` removed from
  `HYGIENE_ROOTS` in `checks/hygiene.py`.
- **Check:** `git ls-files product` prints nothing and `test ! -e product` exits 0. `ls .agents_workspace/product/plans | wc -l` prints
  84 (the 82 plan files plus this plan's two). `git -C .agents_workspace log -1
  --stat` shows the move commit. `python tools/validate-plugins/validate.py` exits 0, and
  with one moved plan's `.md` edited by hand it exits 1 naming that plan, and 0 once
  restored.
- **Status:** todo

### Phase 2: Point every reference at the new path

- **Builds:** Every file in "References that change", root `CLAUDE.md`, `decision-artifact-locations.md`,
  the `docs/STRATEGY.md` line, and the `CHANGELOG.md` entry under the PR's date section. The
  `BACKLOG.md` Source convention, committed in the workspace repo, staging `BACKLOG.md` only,
  as `docs(workspace): backlog paths follow the product move`.
- **Check:** `git grep -n -I -E "(^|[^_./a-z])product/(plans|fixes|retros|ARCHITECTURE)" --
  ':!CHANGELOG.md' ':!archive' ':!audits' ':!plugins' ':!tools/validate-plugins/checks/hooks.py'
  ':!tools/validate-plugins/checks/artifact_paths.py' | grep -v "agents_workspace/product"`
  prints nothing, `git grep -n "product/plans/markdown-formats-yaml" -- tools | grep -v
  "agents_workspace/product"` prints nothing, `grep -n "product/" tools/validate-plugins/README.md
  | grep -v agents_workspace` prints only target-project paths, `grep -n "until a plan moves
  it" .claude/rules/decision-artifact-locations.md CLAUDE.md` prints nothing, and
  `python tools/validate-plugins/validate.py` exits 0.
- **Status:** todo

## Open

- Is losing the CI check of this repo's plans acceptable, given the earlier choice "Yes i
  want ci to catch it" for generated Markdown?: Yes. That choice covered the formats the plugins ship, which CI still checks. This repo's
  plans move to a private repo the public CI cannot read, and the local gate and the render
  hook still check them. A CI job in the agents workspace repo is listed under Out.

## Record

- 2026-11-15 Planned: status ready
- 2026-11-15 Reviewed: Revise first, 1 blocking (artifact_paths.py and hooks.py comments cite this repo's plan but are exempted under Out and by the Phase 2 grep)
- 2026-11-15 PR: #299 https://github.com/cheneeheng/ceh-claude-code-library/pull/299

<!-- prettier-ignore-end -->
