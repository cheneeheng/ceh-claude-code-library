---
schema: plan/v1
title: Give record-project-decisions a scope step, and move each rule's traceability into frontmatter
status: built
created: 2026-10-29
---

## Goal

`ceh-every-session:record-project-decisions` never asks whose decision it is recording, so a
preference that holds across all of a user's work becomes a committed `.claude/rules/decision-*.md`
in whichever repo the session runs in, and no other project sees it. Each rule file also ends with a
`Decided YYYY-MM-DD. Source: ...` tail that loads into every session but only serves a human tracing
the rule. The user asked on 2026-10-29 for both fixes in one plan, and for this repo's three
candidate user-wide rules to move once the scope step exists. After the build, the skill routes each
decision to the project or to `~/.claude/rules/`, the date and source sit in frontmatter that Claude
Code strips before loading, and this repo's rule set holds only what binds this repo.

## Scope

**In:**

- Record and Seed mode decide each decision's scope before writing it: project, user, or one task.
- A user-scope decision is written to `~/.claude/rules/decision-<topic>.md`, never committed, and
  checked for duplicates and contradictions against `~/.claude/rules/decision-*.md` and
  `~/.claude/CLAUDE.md`.
- Seed mode reports any existing project `decision-` file that reads as user-wide, and moves none.
- The skill description, and the docs that describe the skill, cover a preference stated for all
  projects too.
- The decision-rule schema moves to `decision-rule/v2`: `decided` and `source` in frontmatter, the
  body's Why line keeps only the reason.
- The 20 files in `.claude/rules/` are migrated to v2.
- `decision-artifact-locations.md`, `decision-pr-review.md`, and `decision-no-home-paths.md` are
  run through the new scope step, and each one it classes as user scope moves to `~/.claude/rules/`.

**Out:**

- Removing duplication between `~/claude-meta/SOUL.md` and the user rules: SOUL is this user's own
  setup, and the skill must not assume it exists (SOUL priority 1).
- Files that `~/.claude/CLAUDE.md` imports with `@path`: following imports is a reader the skill
  does not need for the common case.
- Renaming the skill to match its wider scope: other skills and docs name it
  (`review-recent-work`, `diagnose-session`, `docs/RETRO_WORKFLOW.md`, `docs/STRATEGY.md`), a
  rename is MAJOR, and project decisions stay its main job.
- A `validate.py` check on the v2 shape: no check reads the Why line today, and a measured miss
  comes first.
- Subfolders in `.claude/rules/`: Claude Code scans them recursively, but the flat layout is a
  separate decision nobody asked to reopen.
- Rewriting `product/retros/2026-10-16-period.md`, which cites `decision-pr-review.md`: a retro is a
  historical record.

## Design

- **Scope test, in Record step 1 and Seed step 4.** Ask: would this hold in a project that is not
  this one? Yes, and it names nothing of this repo (its folders, tools, plugins, or product): user
  scope. It names this repo or its product: project scope. It holds only for the task at hand: not
  a decision, leave it in the conversation. A decision whose user-wide part can stand alone splits
  into a user rule and a project rule that keeps this repo's specifics. Unclear: interactive, ask
  with project scope as the recommended answer. No human: write it at project scope and report the
  scope as open. Reason: project scope is the reversible default, and a committed file is visible
  and reviewable.
- **User-scope home.** `~/.claude/rules/decision-<topic>.md`, same template. Claude Code loads it
  in every project (docs: code.claude.com/docs/en/memory, "User-level rules"), but not in cloud
  sessions or on other machines, so the report names the file and says it is machine-local.
- **Read what exists** (Record step 2) covers `~/.claude/rules/decision-*.md` and, when it exists,
  `~/.claude/CLAUDE.md`. A user decision already stated in `~/.claude/CLAUDE.md` is reported as a
  candidate to move, as the project case does for the project `CLAUDE.md`. A project decision that
  narrows a user one for this project is allowed, and the report names both files. A direct
  contradiction goes to Stop conditions as today.
- **Rules section:** "Committed with the project" becomes "A project decision is committed, a user
  decision never is". The 150-line warning counts unscoped `decision-` files in both folders, since
  both load in every session.
- **Schema v2.** Template:

  ```markdown
  ---
  schema: decision-rule/v2
  decided: YYYY-MM-DD
  source: "<path, conversation, or file (hash)>"
  ---

  # <Topic>

  <rule>

  Why: <reason>.
  ```

  `paths` stays optional, after `source`. `source` is always quoted, because sources hold
  `: ` and backticks, and single-quoted when the value holds a double quote. Claude
  Code reads only `paths` and strips the frontmatter (docs, "Rule frontmatter reference"), so
  `decided` and `source` cost no context. A file with two decision dates keeps the latest in
  `decided`, and `git log` on the file keeps the earlier one. The skill's Output paragraph changes
  from "a file without its `schema:` line gets the template's frontmatter when next edited" to "a
  file below v2 is migrated to v2 when next edited".

- **Migration** is mechanical across 20 files, so a throwaway script in the session scratchpad
  does it: split the `Why:` paragraph at `Decided `, move the date and the `Source:` value into
  frontmatter, keep the reason. It sets `schema: decision-rule/v2`, adds the whole frontmatter
  block when a file has none (`decision-no-home-paths.md`, `decision-pr-review.md`), and places
  `decided` and `source` between `schema` and any existing `paths` block. A tail that is not one
  date then one source is edited by hand: `decision-artifact-locations.md`
  (`Decided 2026-10-22; the three ... subfolders decided 2026-10-23.`), and any file the script
  lists as unmatched.
- **Version:** `ceh-every-session` PATCH (content change, no new skill), with `plugin.json`,
  `marketplace.json`, `CHANGELOG.md` under `## 2026-10-29`, and `docs/PLUGIN_VERSIONS.md`.
- **Docs that describe the skill:** `docs/CATALOG.md` line 21, `ceh-every-session/README.md`
  lines 14 and 31, and their mirror `docs/starlight/src/content/docs/plugins/ceh-every-session.md`
  lines 18 and 35 name the user-scope home alongside the project one.

## Phases

### Phase 1: Scope step and schema v2 in the skill

- **Builds:** the scope test, the user-scope home, the reads of both rule folders and
  `~/.claude/CLAUDE.md`, the Rules changes, the description, schema v2 (template, schema file,
  Output paragraph), and the docs rows. Registration: version bump, changelog, versions table.
- **Check:** `python tools/validate-plugins/validate.py` passes. In
  `plugins/standalone/ceh-every-session/skills/record-project-decisions/`,
  `grep -c "decision-rule/v2" assets/decision-rule.template.md references/decision-rule-schema.md`
  prints at least 1 for each file, `grep -c "~/.claude/rules" SKILL.md` prints at least 1, and
  `grep -L "Decided" assets/decision-rule.template.md` lists the template.
- **Status:** done: the greps print `template.md:1`, `schema.md:2`, `5`, and the template path;
  `validate.py` on a copy of the tracked and new files prints `OK: all plugin checks passed`. The
  starlight page is generated from the README by `docs/starlight/scripts/sync-docs.mjs` and
  git-ignored, so it was not edited.

### Phase 2: Migrate the repo's rules to v2

- **Builds:** the 20 `.claude/rules/decision-*.md` files in v2 shape.
- **Check:** `grep -L "^decided:" .claude/rules/decision-*.md` and
  `grep -l "Decided [0-9]" .claude/rules/decision-*.md` both print nothing;
  `python -c "import glob,yaml; [yaml.safe_load(open(f,encoding='utf-8').read().split('---')[1]) for f in glob.glob('.claude/rules/decision-*.md')]"`
  exits 0; and `validate.py` passes.
- **Status:** done: both greps print nothing, the YAML parse prints `yaml-ok`, and `validate.py`
  prints `OK: all plugin checks passed`. 19 files went through the script and
  `decision-artifact-locations.md` was edited by hand.

### Phase 3: Classify the three candidates

- **Builds:** each of the three files run through the scope test, with the result reported. By the
  test in Design all three are project scope, because each names this repo:
  `decision-no-home-paths.md` names `validate.py`'s `hygiene` check and the repo's folders,
  `decision-artifact-locations.md` names this repo's `product/` and `.agents_workspace/` layout,
  and `decision-pr-review.md` makes `tools/validate-plugins/validate.py` the merge gate. So nothing
  moves unless the user asks for the split of `decision-pr-review.md` (see Open): then a user rule
  "merge your own PRs once CI is green" goes to `~/.claude/rules/decision-pr-review.md`, and the
  repo file keeps only `validate.py` as this repo's gate.
- **Check:** manual: `ls .claude/rules/` still lists all three, and, if the split was asked for,
  `ls ~/.claude/rules/` lists `decision-pr-review.md` and a new session's `/context` shows it under
  Memory files. No command inside this session can show what a fresh session loads.
- **Status:** done: all three classed as project scope, and the user chose no split on 2026-10-29.
  `ls .claude/rules/` lists all three, and `~/.claude/rules/` does not exist.

## Open

- Whether to split `decision-pr-review.md` into a user rule and a project rule: answered
  2026-10-29, no split.
- Cloud sessions and other machines do not see `~/.claude/rules/`: accepted, and the report says
  so.

## Record

- 2026-10-29 Planned: status ready
- 2026-10-29 Reviewed: Revise first, 2 blocking (pr-review moved as-is carries this repo's validate.py gate into every project; double-quoted `source` breaks on artifact-locations' embedded quotes)
- 2026-10-29 Built Phase 1: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-10-29 Built Phase 2: `grep -L "^decided:" .claude/rules/decision-*.md`, prints nothing; YAML parse yaml-ok
- 2026-10-29 Built Phase 3: `ls .claude/rules/`, all three candidates still listed, no split per the user
- 2026-10-29 Checked: 18 Built, 1 Deviation (the starlight mirror was not edited: it is generated from the README and git-ignored)
- 2026-10-29 Design changed: was "`source` is always single-quoted, per `decision-frontmatter-scalars.md`", now "`source` is always quoted, ... single-quoted when the value holds a double quote", because the pre-commit prettier hook rewrites single quotes to double unless the value holds one
