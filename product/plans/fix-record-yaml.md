---
schema: plan/v2
generated_from: fix-record-yaml.yaml
generated_note: "Do not edit. artifact.py renders this file from fix-record-yaml.yaml: edit the YAML, then run artifact.py render."
title: The fix record as a YAML format, fix-record/v2
status: built
created: 2026-11-10
---

<!-- prettier-ignore-start -->

## Goal

Phase 4 of `product/plans/report-only-formats.yaml`: the fix record that
`ceh-coding-conduct:find-root-cause` writes and `ceh-testing:test-a-bug-fix` completes becomes a
YAML format checked by a pydantic model, as the six reports before it, because it is a handoff
between two skills and a later session, which the user's instruction to make handoff files
deterministic and checkable covers. The flow that matters: `find-root-cause` saves
`product/fixes/<slug>.yaml` with `status: diagnosed` and no confirmed hypothesis, the hook reports
`diagnosis.rows` right after the write, and `test-a-bug-fix` later finds the diagnosed record,
checks it, adds the fix and the tests, sets `status: fixed`, and the Markdown beside it renders in
the `fix-record/v1` layout.

## Scope

**In:**

- `fix-record/v2`: `product/fixes/<slug>.yaml` validated by `fix-record-model.py`, with
  `product/fixes/<slug>.md` rendered beside it in the `fix-record/v1` layout, and the status
  rules of Design "Rules the model enforces" refused as errors.
- `ceh-coding-conduct` gains the render hook and the generated-Markdown guard, so a fix record
  is checked on every write whether or not `ceh-testing` is installed.
- `test-a-bug-fix` completes an uncommitted `diagnosed` `.yaml` record, or creates a `fixed`
  one, checked and rendered, and still completes a `diagnosed` `v1` `.md` record with no YAML
  beside it in the `v1` form.
- `find-root-cause` saves the record as `fix-record/v2` and renders it.
- Repo upkeep in the phase that causes each piece: copies registered in
  `docs/CROSS_REFERENCES.md` per Design "Rendering and files", hook fixtures in
  `tools/validate-plugins/checks/hooks.py`, both plugin READMEs naming the YAML beside its
  Markdown and uv, `docs/GETTING_STARTED.md` naming `python3` and uv for
  `ceh-coding-conduct`'s hooks, `docs/STRATEGY.md` naming the record's YAML,
  `docs/ENVIRONMENT_VARIABLES.md` adding `ceh-coding-conduct` to `CEH_ARTIFACT_CHECK`, uv in
  the `compatibility` of both skills, `decision-artifact-validation.md` and
  `decision-output-templates.md` listing `fix-record/v2`, and per PR the changelog, the version
  bumps in `plugin.json` and `.claude-plugin/marketplace.json`, and `docs/PLUGIN_VERSIONS.md`.
- Phase 4 of `product/plans/report-only-formats.yaml` set `done`, with this plan as its
  evidence.

**Out:**

- Moving the five `fix-record/v1` records in this repo's `product/fixes/` to YAML.: They are finished history (`fixed` is final), nobody edits them again, and both skills
  still read a `v1` record. A record in a user's repo stays `v1` for the same reason.
- A new reader of fix records, such as an evidence-report area or a retro input.: No skill reads them beyond these two today, and `find-root-cause` step 2 greps
  `product/fixes/` for a file name, which the generated `.md` and the YAML both still match.
- The session handoff and the Phase 6 formats.: Phases 5 and 6 of `product/plans/report-only-formats.yaml`, each planned on its own.
- A `ceh-coding-conduct` dependency on `ceh-testing`, or the reverse.: The handoff stays prose, as `decision-plugin-dependencies.md` asks for a conditional
  handoff, and each plugin carries its own copy of the model.
- The Starlight pages for the two plugins.: `docs/starlight/src/content/docs/*` is git-ignored and built from the plugin READMEs, which
  In item 5 updates.

## Design

- **Keys** Each required unless marked optional, and no other key:

  - `schema`: `fix-record/v2`. `status`: `diagnosed`, `fixed` or `unreproduced`. `date`: an
    unquoted date. `issue`: optional, as in `v1`. `plan`: optional, starts with
    `product/plans/`. `previous`: optional, the earlier record's `.md` path under
    `product/fixes/`, which exists for both versions and is what `find-root-cause` step 2
    greps.
  - `title`: the behavior that was wrong.
  - `symptom`: `command` (optional) and `output`. For an `unreproduced` record, `output` is the
    reported failure, since no command produced one.
  - `diagnosis`: one model with `rows` and `known_from_report` both optional and a validator
    that requires exactly one, so `model_vs_template.py` sees one object, and
    `fix-record.template.yaml` lists both keys. `rows`: at least one, each with `hypothesis`,
    `refuted_by`, `result` (`refuted`, `standing` or `confirmed`) and `output`. In an
    `unreproduced` record each attempt is a row whose hypothesis reads "it reproduces under
    <condition>". `known_from_report`: where the report names the cause, such as `issue #12`.
  - `cause`: optional, `location` (the `file:line` or condition, or for a fix that lands
    elsewhere, the package and version or the setting) and `chain`, one sentence.
  - `prediction`: a list, `[]` when none, each with `command` (optional) and `result`, the
    result predicted and then seen, so the two records holding two predictions fit.
  - `fix`: optional, text. `tests`: a list, `[]` when none, each with `test`, `protects`,
    `fails_when` and `why_new`.
  - `unverified`: text, `none` when nothing stayed unrun.
- **Rules the model enforces**
  - `diagnosed`: `cause` set, no `fix`, `tests` empty, `rows` with at least one `confirmed`.
  - `fixed`: `cause`, `fix` and at least one test set. With `rows`, at least one `confirmed`.
    `known_from_report` is allowed only here, the case the `v1` rule names.
  - `unreproduced`: `rows`, none `confirmed`, and no `cause`, `fix` or `tests`, and
    `prediction` empty.
  - One-line fields hold no newline: `title`, both `symptom` keys, every `rows` key,
    `cause.location`, each `prediction` key, and each test's four keys, so the table cells,
    the `**Symptom:**` line and the test bullets render whole.

  These are the `v1` "Sections by status" rules made checkable. `status moves forward only`
  and `same commit` stay prose rules, because they compare a record with its history, which
  one file cannot show.
- **Rendering and files** `fix-record-model.py` holds the model and `render(doc, source)`, writing the `v1` layout of
  `fix-record.template.md` with `generated_from` and the do-not-edit `generated_note` in its
  frontmatter and the body in a prettier-ignore range, as the six reports do:

  - `**Symptom:**` then the command as a code span, `→` and the output, or the output alone
    with no command.
  - The diagnosis table, each Result cell `<result>: <output>`, with `|` escaped in every
    cell as `security-audit-model.py` `_cell` does. With `known_from_report`, the table is
    replaced by `Cause known from the report: <known_from_report>`, and `**Cause:**` still
    renders below it.
  - `**Cause:** <location>: <chain>`, and `**Prediction:**` with one sentence per item: the
    command as a code span, `→` and the result, or the result alone with no command.
  - `## Fix`, `**Tests:**` and `**Unverified:**` as in `v1`, sections a status does not keep
    left out, as `v1` "Sections by status" says.

  The model and `fix-record.template.yaml` sit beside the schema in `find-root-cause`
  (canonical) and `test-a-bug-fix` (copies), byte-identical, added to the existing "Fix record
  format" entry of `docs/CROSS_REFERENCES.md` (its Canonical line and copy rows), which keeps
  the `v1` template as the rendered Markdown's shape. The two skill copies of
  `scripts/artifact.py` and the three `ceh-coding-conduct` root scripts are rows in the
  "Build plan format" entry, where every other copy of those scripts is registered, so the
  `copies` check keeps them identical.
- **Hooks in ceh-coding-conduct** `artifact.py`, `artifact-render-hook.py` and `generated-md-guard.py` copied to
  `plugins/standalone/ceh-coding-conduct/scripts/`, and PreToolUse and PostToolUse
  `Edit|Write|MultiEdit` entries added to the existing `hooks/hooks.json`, beside its
  SessionStart, SubagentStart and UserPromptSubmit entries, in the shape
  `ceh-security-audit/hooks/hooks.json` uses. The user chose this on 2026-11-10 over listing
  the plugin in `READERS` and having the skill render alone, so a record is checked on every
  write even without `ceh-testing`. The cost, measured once on Windows: about 85 ms per Edit or
  Write for the two hooks together on an ordinary file, in every coding session, and a
  `python3` requirement the plugin did not have. With `ceh-testing` installed too, a fix
  record is checked by both plugins and an error is reported twice, as the security audit is
  today.
- **Reading a v1 record** `test-a-bug-fix` looks for an uncommitted record with `git status --porcelain
  product/fixes/`. A `.yaml` is checked with `artifact.py check` first (stop on exit 1 with
  its errors), edited by key and rendered. A `.md` with no `.yaml` beside it is a `v1` record,
  completed in the `v1` form as today, because moving it mid-fix would change two formats in
  one commit. Without uv, the YAML is edited unchecked and the reply says so, as the other
  formats do.
- **Versions and pull requests** One PR per phase. Phase 1 bumps `ceh-coding-conduct` MINOR, because it gains hooks, as
  `ceh-security-audit` went to 1.1.0 and `ceh-usability-audit` to 1.2.0 when they did, and
  `ceh-testing` PATCH. Phase 2 bumps `ceh-coding-conduct` PATCH.

## Phases

### Phase 1: The format, the hooks, and the reader

- **Builds:** Scope In items 1, 2 and 3, with Phase 1's share of item 5: `fix-record-model.py`,
  `fix-record.template.yaml`, and a `fix-record/v2` section added to `fix-record-schema.md`
  beside its `v1` text, as `plan-schema.md` holds both plan versions, in both skills (the
  canonical files in `find-root-cause`, whose body keeps writing `v1` until Phase 2);
  `scripts/artifact.py` in both skills; the `ceh-coding-conduct` root scripts and hook entries
  per Design "Hooks in ceh-coding-conduct"; `test-a-bug-fix` reading and completing both
  versions per Design "Reading a v1 record", with uv in its `compatibility`; the registry rows;
  the fixtures for both plugins; both READMEs; `GETTING_STARTED.md`; the
  `CEH_ARTIFACT_CHECK` row; and the two version bumps with the changelog. The reader and the
  hooks ship before the writer, so no installed version writes a record its partner cannot
  read.
- **Check:** With uv, a scratchpad `product/fixes/x.yaml` for each status, plus a `fixed` one with
  `known_from_report` and one with two predictions, renders (exit 0) to Markdown whose body
  matches the `v1` layout section by section, and one file per rule in Design "Rules the model
  enforces" exits 1 naming its field path (a `diagnosed` record with a test names `tests`, an
  `unreproduced` one with a `confirmed` row names `diagnosis.rows`, a `diagnosis` with both
  keys names `diagnosis`). `git grep -n -e "artifact.py check" -e "git status --porcelain
  product/fixes/" -e "no .yaml beside it" --
  plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md` matches all three.
  `python tools/validate-plugins/validate.py`, whose fixtures render a good `fix-record/v2`
  file and block a bad one through each plugin's render hook, print "uv is not installed"
  without uv, stay silent on a file with no `schema:` key, and have the `ceh-coding-conduct`
  guard deny an edit to a generated `.md`, prints "OK: all plugin checks passed".
- **Status:** done, Scratchpad records `diagnosed`, `fixed`, `fixed` with `known_from_report` and `unreproduced`
  (one with two predictions) rendered with exit 0 in the `v1` layout. Six bad records exited 1
  naming `diagnosis`, `cause`, `diagnosis.rows` (twice) and `tests` (twice). The three greps
  each matched once in `test-a-bug-fix/SKILL.md`. The two copies of each of the four format
  files share an md5. `python tools/validate-plugins/validate.py` printed "OK: all plugin
  checks passed", and a fixture with a wrong marker made it fail on
  `count-drops-last-word.md was not rendered`. The third grep pattern is written in the skill as "no `.yaml` beside it", with backticks, so
  the check ran `git grep -F` with that exact text instead of the regex the Check names.

### Phase 2: The writer

- **Builds:** Scope In items 4 and 6, with Phase 2's share of item 5: `find-root-cause` steps 8 and 9 and
  its Output saving `product/fixes/<slug>.yaml`, running `artifact.py render`, and editing a
  `diagnosed` record by key when no `ceh-testing` completes it, with uv in its
  `compatibility`; `docs/STRATEGY.md`; the two rule files; the `ceh-coding-conduct` version
  and the changelog; then `report-only-formats.yaml` Phase 4 set `done`.
- **Check:** `git grep -n -e "product/fixes/<slug>.yaml" -e "artifact.py render" -e "compatibility:" --
  plugins/standalone/ceh-coding-conduct/skills/find-root-cause/SKILL.md` matches all three, and
  `git grep -n "product/fixes/<slug>.md" -- plugins/standalone/ceh-coding-conduct/skills/find-root-cause/SKILL.md`
  prints no line in step 8. `git grep -n "fix-record/v2" -- docs/STRATEGY.md
  .claude/rules/decision-artifact-validation.md .claude/rules/decision-output-templates.md`
  matches each file. `uv run --script plugins/standalone/ceh-build-planning/scripts/artifact.py
  check product/plans/report-only-formats.yaml` exits 0. `python
  tools/validate-plugins/validate.py` prints "OK: all plugin checks passed".
- **Status:** done, The three greps matched `find-root-cause/SKILL.md`, step 8 holds no
  `product/fixes/<slug>.md`, `fix-record/v2` matched the three docs, the
  `report-only-formats.yaml` check exited 0, and `python tools/validate-plugins/validate.py`
  printed "OK: all plugin checks passed". The `ceh-testing` README row named the old `.md` path too, so `ceh-testing` took a PATCH
  bump in this phase, as Design "Versions and pull requests" allows.

## Open

None

## Record

- 2026-11-10 Planned: status ready
- 2026-11-10 Reviewed: Revise first, 2 blocking (Phase 1 carried a model in ceh-coding-conduct without its hook
  scripts, which validate.py rejects; Phase 2's grep passed before any edit), all fixed with
  the 10 advisory findings, the owner question answered by the user: hooks in
  ceh-coding-conduct
- 2026-11-10 PR: #236 https://github.com/cheneeheng/ceh-claude-code-library/pull/236
- 2026-11-10 Built Phase 1: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-10 PR: #237 https://github.com/cheneeheng/ceh-claude-code-library/pull/237
- 2026-11-10 Built Phase 2: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-10 Checked: 19 Built (6 In, 6 Design, 5 Out absent, 2 phase Checks rerun), 0 Gap, 0 Deviation, 0 Extra,
  0 Failing, 0 Cannot verify

<!-- prettier-ignore-end -->
