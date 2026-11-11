---
schema: plan/v2
generated_from: report-only-formats.yaml
generated_note: "Do not edit. artifact.py renders this file from report-only-formats.yaml: edit the YAML, then run artifact.py render."
title: YAML formats for the reports another stage reads, and why the rest stay Markdown
status: building
created: 2026-11-10
---

<!-- prettier-ignore-start -->

## Goal

Phase 7 of `product/plans/artifact-validation-formats.yaml` asks for this plan: the report-only
formats, format by format, each with its case under VISION principle 7. The case that carried the
spine files, the user's instruction to make handoff artifacts deterministic and checkable (VISION,
Who overrides), covers a report only when another skill or a later session reads it. A report
only its author or a human reads needs a failure the prose did not prevent, and none is recorded
in `product/retros/` or `product/fixes/`. So this plan converts the reports
`ceh-testing:write-evidence-report` reads to prove product claims (QA, performance, security and
the three usability audits), lists the other handoff reports as later phases planned once this
slice is judged, and keeps every other format in Markdown with its reason. The flow that matters
most: `explore-app-for-bugs` saves `QA_REPORT.yaml` with a charter naming bug `B3` that the file
does not hold, the `ceh-testing` hook reports `charters.0.bugs` to the agent right after the write,
and `write-evidence-report` later reads `commit` and `bugs` by key from a file whose every field
was checked.

## Scope

**In:**

- `qa-report/v2`: `QA_REPORT.yaml` validated by `qa-report-model.py`, with `QA_REPORT.md`
  rendered beside it in the `qa-report/v1` layout, written by
  `ceh-testing:explore-app-for-bugs`.
- `perf-report/v2`: `<metric>.yaml` validated by `perf-report-model.py`, with `<metric>.md`
  rendered in the `perf-report/v1` layout and the `vs baseline` column computed by the renderer,
  written by `ceh-testing:measure-performance`, which moves a `v1` `<metric>.md` on its next
  attempt.
- `security-audit/v2`: `SECURITY_AUDIT-<date>.yaml` validated by `security-audit-model.py`, with
  the Markdown rendered in the `security-audit/v1` layout, written by
  `ceh-security-audit:audit-codebase-security`, with the render hook and generated-Markdown
  guard added to `ceh-security-audit`.
- `first-run-audit/v2`, `interface-audit/v2` and `error-messages-audit/v2`: the three usability
  audits as YAML, each gaining a required `commit`, rendered in their `v1` layouts, written by
  `simulate-newcomer-first-run`, `audit-interface` and `audit-error-messages`, with the hooks
  added to `ceh-usability-audit`.
- `write-evidence-report` carrying all six models and reading each report's YAML by key path,
  with `commit` as the commit the report ran against, and the Markdown when no YAML exists.
- Repo upkeep in the phase that creates each copy: hook fixtures in `checks/hooks.py`, copies
  registered in `docs/CROSS_REFERENCES.md`, the plugin READMEs naming uv, the
  `docs/starlight/src/content/docs/plugins/ceh-testing.md` and `ceh-usability-audit.md` pages
  naming each report's YAML beside its Markdown,
  `decision-artifact-validation.md` and `decision-output-templates.md` listing the new formats,
  and a version bump per plugin.

**Out:**

- The fix record (`find-root-cause` to `test-a-bug-fix`): A handoff, so the user's instruction covers it, but its fields need their own design. Phase
  4, `unplanned` until the user judges Phases 1 to 3.
- The session handoff (`hand-off-session` save to load, and `whats-next`): A handoff to a later session. Phase 5, `unplanned` for the same reason.
- The workflow spec and run state, competitor report, glossary, blog voice and repeat-mistake report: Each has a reader in another skill or a later session (`build-agentic-workflow`,
  `run-agentic-workflow`, `compare-competitors`, `record-project-decisions`, `edit-post`, and
  `prevent-repeat-mistake` step 1, which lists the fixes still `awaiting approval`). Phase 6,
  `unplanned`, one plan per format once Phases 1 to 3 are judged.
- Report-only formats (plan review, code review, business plan review, test audit, stress test, research note, codebase explained, refactor report, learning, period retro, session retro, competitor comparison, decision log, orchestration-lab run and runs index): Only the author or a human reads them, and no failure of their prose is recorded, so
  principle 7 gives no case for enforcement. `review-recent-work` takes only the date in a
  period retro's file name, never its content. `session-retro` issues reach
  `prevent-repeat-mistake` through the conversation, not by reading the file. Each is revisited
  when a session shows its format failing.
- The blog draft, repurposed post, investor deck and investor outreach: They are what the user ships, which `decision-output-templates.md` puts out of scope.
- The questionnaire: A person writes the answers into the file, and a YAML source with a guarded Markdown would
  make that person edit YAML.
- The decision rule: Claude Code reads `.claude/rules/*.md` itself, so the Markdown must stay the source.
- The workflow approval and draft questions: Read only inside the build that writes them, so they are report-only.
- Moving older QA, security and usability reports to YAML: Each describes one run and is never updated, so an older one stays as written, as the trial
  left `plan/v1` plans, and `write-evidence-report` reads its Markdown. The performance file is
  the exception, kept per metric, and Design moves it.

## Design

- **Why the vision allows it** The six reports are handoff files: `write-evidence-report` reads each one to decide which
  product claims may be made, so a wrong commit or a miscounted severity becomes a false claim
  in `product/EVIDENCE.md`. The user's instruction covers them as it covered the spine. The
  usability audits name no commit today, so `write-evidence-report` takes "the last commit
  before its date", a guess the required `commit` field removes. The formats under Out have
  no reader in another skill, or a reason of their own, and stay Markdown.
- **One mechanism, unchanged** Each format copies the pieces of `artifact-validation-formats.yaml` as they are:
  `<name>-model.py` beside `<name>-schema.md`, `<name>.template.yaml` in `assets/`,
  `scripts/artifact.py` in each skill that carries the model, and `artifact.py`,
  `artifact-render-hook.py` and `generated-md-guard.py` at the root of each writer plugin, wired
  in `hooks/hooks.json`. Each model sets `extra="forbid"` and `strict=True`, renders
  frontmatter with `schema`, `generated_from` and `generated_note` first, and keeps the `v1`
  layout so a reader that greps the Markdown sees no change. The hook finds a report by its
  `schema:` key, so `place_format` gains no entry: a report YAML is never mistaken for a spine
  file, and a report YAML that lost its `schema:` key is skipped, which the read-time check in
  `write-evidence-report` then catches. Because the hook acts on every model in its plugin,
  `ceh-testing`'s hook also checks security and usability YAML through
  `write-evidence-report`'s copies, so with both plugins installed an error is reported twice.
  This is accepted, as it is for the plan copies, because both verdicts come from the same
  model, and a version lag between copies shows as a block naming the file, never a silent pass.
  Every `commit` field in every model, `kept_commit` and `fix.commit` included, matches
  `^[0-9a-f]{7,40}$`, because `write-evidence-report` runs `git log <commit>..HEAD` on it.
- **The qa-report/v2 model** `{schema, app, commit, mode: report | fix, date: "YYYY-MM-DD HH:MM", launched_with: {command,
  entry}, charters: list of {charter, actions_used: int 0 to 20, bugs: list of str}, bugs: list
  of {id, severity: Critical | Major | Minor | Cosmetic, title, status: confirmed | unconfirmed,
  steps: list of str, at least one, expected, actual, evidence, fix: {commit, rerun} optional},
  usability_notes: list of str, not_explored: list of {what, why}}`. Validators: bug ids are unique, every id a charter names is a bug in the
  file, and `fix` is allowed only when `mode` is `fix`.
- **The perf-report/v2 model** `{schema, metric, commit, command, machine, input, unit, spread: range | iqr, attempts: list
  of {attempt, change, median: float, low: float, high: float, within_noise: bool, kept: bool,
  kept_commit: str optional}}`, at least one attempt. `spread` says whether `low` and `high` are
  the min and max or the interquartile range, as v1 allows either. Validators: the first attempt
  is `baseline` and only the first, `low <= median <= high`, `within_noise` and `kept` are false
  on the baseline, its median is above 0, and `kept_commit` is required exactly when `kept` is
  true. The renderer writes
  `vs baseline` as `no measurable change` when `within_noise` is true, and otherwise as the
  signed percent change of the median from the baseline's to one decimal, so no model does that
  arithmetic. `unit` is new, and renders after each median.
- **Moving a performance file** `<metric>.md` is kept per metric and gains attempts across sessions, so it is a living file.
  When `measure-performance` finds a `perf-report/v1` `<metric>.md` with no YAML beside it, it
  copies it to `<metric>.v1.md` first, because `.agents_workspace/` is not in git, writes
  `<metric>.yaml` from its frontmatter and table (a spread it cannot tell is `range`, a `vs
  baseline` cell reading `no measurable change` sets `within_noise`), renders, and only then
  adds the new attempt. The reply names the move and the backup.
- **The security-audit/v2 model** `{schema, repo, commit, date, attack_surface: str, findings: list of {severity: critical |
  high | medium | low, confidence: confirmed | likely, category, attacker, location, attack,
  fix}, possible: list of {lead, settle}, not_checked: list of {check, reason, command}}`.
  `location` matches `^[^\s:]+:\d+$`. The renderer numbers the findings, so no number is stored.
- **The usability audit models** All three gain a required `commit`, which the user chose on 2026-11-10, because without it
  `write-evidence-report` guesses the commit from the date, and the guess is wrong whenever two
  commits land on one day. `run` is an int, rendered zero-padded to three digits
  (`007`) to match the `run-<NNN>` folder.

  The first-run and interface audits share a finding, `{id, severity: Blocker | Detour |
  Friction | Polish, title, where, persona, expected, got, fix}`, with `missing_knowledge`
  required in `first-run-audit/v2` only, finding ids unique, and a gate `{score: int, out_of:
  int, na: int}` with `score <= out_of` and `out_of + na == 5`, rendered `<score>/5` when `na`
  is 0 and `<score>/<out_of>, <na> N/A` otherwise, as v1 writes it. `first-run-audit/v2` holds
  `{target, run, date, commit, goal, milestones: list of {name, budget: int}, audience,
  frozen_set, walkers: {run: list of str, skipped: list of {persona, why}, mode: in parallel |
  serially | in isolated copies}, gate, results: list of {persona, furthest, stop_reason,
  actions: int, budget: int, lookups: int, wait_s: int, first_stall: str optional}, minutes: int,
  findings, hypotheses: list of str, not_covered: list of str}`. Each result's `budget` is the
  budget of the milestone it was walking, rendered `<actions>/<budget>`, and the machine wait
  after the time estimate is the sum of every `wait_s`, computed by the renderer. A validator
  checks that each `first_stall` names a finding. `interface-audit/v2` holds `{target, surface,
  run, date, commit, goals: list of {goal, budget: int}, audience, allowlist, walkers: {run:
  list of str, skipped: list of {persona, why}}, gate, five_questions: list of {screen,
  where_am_i, what_for, primary_action, what_happened, way_out}, findings, hypotheses,
  delegated: list of {skill, what}, not_covered}`, with no `mode`, since the v1 layout has none.

  The error-messages audit has no gate and no findings. `error-messages-audit/v2` holds
  `{target, run, date, commit, harvested: int, already_complete: int, rows: list of {location,
  current, checks: list of exactly three bools, severity: Blocker | Detour | Friction | Polish,
  rewrite, applied: bool, reason: str optional}, systemic: list of {handler, rows: list of int,
  fixed: bool}}`, rows numbered by the renderer from 1, with validators: `already_complete <=
  harvested`, `reason` required exactly when `applied` is false, and each `systemic` row number
  names a row.
- **Who carries what**
  | Format | Model in | Hooks in |
  | --- | --- | --- |
  | qa-report | `ceh-testing:explore-app-for-bugs`, `ceh-testing:write-evidence-report` | `ceh-testing` (already) |
  | perf-report | `ceh-testing:measure-performance`, `ceh-testing:write-evidence-report` | `ceh-testing` (already) |
  | security-audit | `ceh-security-audit:audit-codebase-security`, `ceh-testing:write-evidence-report` | `ceh-security-audit` |
  | first-run-audit, interface-audit, error-messages-audit | their writer skill each, `ceh-testing:write-evidence-report` | `ceh-usability-audit` |

  No `dependencies` entry is added: `write-evidence-report` carries its own copies, so each
  plugin still works installed alone.
- **write-evidence-report reads by key** For each area, when the report's `.yaml` sits beside its `.md`, the skill runs `artifact.py
  check` first and reads `commit` as the commit the report ran against, then QA's `bugs` (with
  `severity` and `fix`), performance's `attempts` (the last `kept` one, else the baseline),
  security's `findings` by `severity`, the first-run and interface audits' `findings` and
  `gate`, and the error-messages audit's `rows` (`severity`, `applied`), `harvested` and
  `already_complete`. Two usability formats share the file name `UX_AUDIT`, so the skill picks
  the model by the file's `schema:` key and keeps the newest of each format per target. Exit 1
  on a report marks that area `not run`, naming the errors, because a broken report proves
  nothing. Exit 3 means a version this copy does not know, so the skill reads that report's
  Markdown instead and says so, because v2 key paths may not hold in it. Exit 2, or no uv, is
  said in the reply as "not checked", and the skill reads the YAML anyway. With no YAML, it
  reads the Markdown as today.
- **Landing** Each phase lands as its own PR with its `CHANGELOG.md` entry and `docs/PLUGIN_VERSIONS.md`
  rows. A plugin that gains hooks bumps MINOR, every other plugin a phase touches bumps PATCH.
  Phase 7 of `artifact-validation-formats.yaml` is marked done with this plan's path as its
  evidence once this plan is reviewed, since its Check asks only for that, which makes that plan
  `built`.

## Phases

### Phase 1: QA and performance reports

- **Builds:** `qa-report-model.py`, `perf-report-model.py`, their templates and `v2` schema sections in
  `explore-app-for-bugs` and `measure-performance`, each with `scripts/artifact.py`; both skills
  saving the YAML, checking it before an edit and rendering it after; `measure-performance`
  moving a `v1` `<metric>.md` per Design; copies of both models in `write-evidence-report`,
  which reads the QA and performance YAML by key per Design; fixtures, copies registered, docs
  rows.
- **Check:** In the scratchpad, a filled `QA_REPORT.yaml` and `<metric>.yaml` render through `uv run
  --script plugins/standalone/ceh-testing/scripts/artifact.py render`, and their lines starting
  `#`, `|` and `**` equal the `v1` templates' with values ignored; the rendered `vs baseline`
  of a 120 ms baseline and a 90 ms attempt reads `-25.0%`, and of an attempt with
  `within_noise: true` reads `no measurable change`. Each exits 1 naming its field path: a
  charter naming a missing bug, a `fix` in `report` mode, a second `baseline`, `low` above
  `median`, `kept: true` with no `kept_commit`, a `commit` of `HEAD`. A scratchpad script
  resolves every key path `write-evidence-report` names for QA and performance through each
  copy's `model_json_schema()`, and `grep -n "artifact.py check"` and `grep -n "not run"` find
  the read step in its `SKILL.md`. `python tools/validate-plugins/validate.py` is green.
- **Status:** done, a scratchpad `QA_REPORT.yaml` (fix mode, one bug) and `latency.yaml` (three attempts) rendered
  (exit 0), and a script comparing their `#`, `|` and `**` lines with the `v1` templates printed
  SAME for both; the rendered `vs baseline` cells read `-25.0%` for 120 to 90 ms and `no
  measurable change` for `within_noise: true`; the six planted copies each exited 1, naming
  `charters.0.bugs`, `bugs.0.fix`, `attempts.2 is a second baseline`, `attempts.1` (low above
  median), `attempts.1` (kept_commit) and `commit`; a key-path script resolved 5 QA and 9
  performance paths through both copies of each model, 0 missing, and failed on a planted
  `bugs.0.nope`; `grep -n` found `artifact.py check` at line 55 and `not run` in the read step
  of `write-evidence-report/SKILL.md`; `python tools/validate-plugins/validate.py` printed "OK:
  all plugin checks passed". The Starlight page `docs/starlight/src/content/docs/plugins/ceh-testing.md` is git-ignored and
  built from the plugin README, so the README's rows name `QA_REPORT.yaml` for it. The template
  shows one generic attempt, because `model_vs_template.py` compares only a list's first item,
  and the baseline has no `kept_commit`.

### Phase 2: Security audit

- **Builds:** `security-audit-model.py`, template and `v2` schema section in `audit-codebase-security` with
  `scripts/artifact.py`; the plugin-root scripts and `hooks/hooks.json` in `ceh-security-audit`;
  the skill saving and re-checking the YAML; the copy in `write-evidence-report` and its read by
  key; fixtures, copies registered, docs rows.
- **Check:** A filled `SECURITY_AUDIT-<date>.yaml` with three findings renders with the findings numbered 1
  to 3. Each exits 1: a severity `severe`, a `location` with no line number, an unknown key.
  Piped to the `ceh-security-audit` hook, a Write of that YAML with a bad severity is blocked
  naming `findings.0.severity`. A scratchpad script resolves every security key path
  `write-evidence-report` names through its copy's `model_json_schema()`. `python
  tools/validate-plugins/validate.py` is green.
- **Status:** done, a scratchpad `SECURITY_AUDIT-2026-11-10.yaml` with three findings rendered (exit 0), its rows
  numbered 1, 2 and 3 and its `#`, `|` and `**` lines equal to the `v1` template's (SAME); the
  three planted copies each exited 1, naming `findings.0.severity`, `findings.1.location` and
  `owner` (extra input); the `ceh-security-audit` hook fixture blocking a bad severity naming
  `findings.0.severity` passed in `checks/hooks.py`; a key-path script resolved 4 security
  paths through both copies, 0 missing; `python tools/validate-plugins/validate.py` printed
  "OK: all plugin checks passed".

### Phase 3: Usability audits

- **Builds:** The three models, templates and `v2` schema sections in their writer skills, each with
  `scripts/artifact.py`; the plugin-root scripts and `hooks/hooks.json` in `ceh-usability-audit`;
  the three skills saving and re-checking the YAML with `commit` set; the copies in
  `write-evidence-report`, which takes each audit's commit from `commit` instead of the date;
  fixtures, copies registered, docs rows.
- **Check:** A filled YAML of each audit renders with headings equal to its `v1` template's, `run: 7` as
  `007`, and the first-run and interface gates as `4/5` with `na: 0` and `4/4, 1 N/A` with `na:
  1`. Each exits 1: no `commit`, a gate with `out_of + na` of 4, a `first_stall` naming no
  finding, `already_complete` above `harvested`, `applied: false` with no `reason`, `checks`
  with two bools. Piped to the `ceh-usability-audit` hook, a Write of a `UX_AUDIT.yaml` with no
  `commit` is blocked naming `commit`, once with each of the two `UX_AUDIT` schemas. A
  scratchpad script resolves every usability key path `write-evidence-report` names through
  each copy's `model_json_schema()`. `python tools/validate-plugins/validate.py` is green.
- **Status:** done, one scratchpad YAML per audit rendered (exit 0), each with its `#`, `|` and `**` lines equal
  to its `v1` template's (SAME, three times); `run: 7` rendered `007`, the first-run gate `4/5`
  with `na: 0` and the interface gate `4/4, 1 N/A` with `na: 1`, and the machine wait summed to
  `20s`; the planted copies each exited 1, naming `commit` (first-run and interface), `gate`
  (out_of + na of 4), `results.0.first_stall`, `already_complete`, `rows.1` (no reason) and
  `rows.0.checks` (two bools); the `ceh-usability-audit` hook fixtures blocking a
  `UX_AUDIT.yaml` with no `commit` under each of the two schemas passed in `checks/hooks.py`; a
  key-path script resolved 20 usability paths through both copies of each model, 0 missing;
  `python tools/validate-plugins/validate.py` printed "OK: all plugin checks passed".

### Phase 4: Fix record

- **Builds:** `fix-record/v2` as YAML, written by `find-root-cause` and read by `test-a-bug-fix`.
- **Check:** Planned once Phases 1 to 3 are judged.
- **Status:** done, Built by its own plan, `product/plans/fix-record-yaml.yaml`, in PRs #237 and #238, each with `python tools/validate-plugins/validate.py` printing "OK: all
  plugin checks passed". Planned and checked in `product/plans/fix-record-yaml.yaml`, whose phases hold the real
  Checks, because a building plan's unplanned phase gets its own plan file.

### Phase 5: Session handoff

- **Builds:** `handoff/v2` as YAML, written and loaded by `hand-off-session` and read by `whats-next`.
- **Check:** Planned once Phases 1 to 3 are judged.
- **Status:** done, Built by its own plan, `product/plans/handoff-yaml.yaml`, in PR #240, with `python
  tools/validate-plugins/validate.py` printing "OK: all plugin checks passed". Planned and checked in `product/plans/handoff-yaml.yaml`, whose phase holds the real Check.

### Phase 6: Other handoff reports

- **Builds:** One plan per format for the workflow spec, run state, competitor report, glossary, blog voice
  and repeat-mistake report, each with its reader named.
- **Check:** All six linked plans exist, name their readers and have completed plan reviews. Check each with
  `uv run --script plugins/standalone/ceh-build-planning/scripts/artifact.py check <plan.yaml>`.
  Every check exits 0. This phase delivers plans; the child plans track their implementations.
- **Status:** todo. The workflow spec is planned and built by `product/plans/workflow-spec-yaml.yaml`
  (`workflow-spec/v2`), the run state by `product/plans/run-state-yaml.yaml`
  (`run-state/v2`), and the competitor report by `product/plans/competitor-report-yaml.yaml`
  (`competitor-report/v2`), and the glossary by `product/plans/glossary-yaml.yaml`
  (`glossary/v2`, reader record-project-decisions). The remaining formats are planned in
  `product/plans/blog-voice-yaml.yaml` (`blog-voice/v2`, readers draft-post and edit-post),
  and `product/plans/repeat-mistake-yaml.yaml` (`repeat-mistake/v2`, reader
  prevent-repeat-mistake step 1). These two are planned, not implemented. Build in that
  order, preserving earlier shared hook additions and rebasing version/bookkeeping changes
  on the current branch. Each format lands separately if landing is authorized.
  All six plan checks passed on 2026-11-11. The Built record is not yet written.

## Open

- What does a usability audit of a target outside git put in its required `commit`?: Nothing yet: the three audits read `git rev-parse --short HEAD` in the target, and every
  target walked so far is a git repo. If one is not, the report fails its check and the reply
  says so, and the format gets an optional `commit` then, once a real run shows it.

## Record

- 2026-11-10 Planned: status ready
- 2026-11-10 Reviewed: Revise first, 7 blocking (gate drops the N/A form, error-messages audit given a gate and findings it lacks, perf model cannot say no measurable change or an IQR spread, perf file treated as never updated, Results budget and total wait underived, Checks never prove the reader, repeat-mistake report has a later-session reader), all fixed with the 6 advisory findings
- 2026-11-10 PR: #226 https://github.com/cheneeheng/ceh-claude-code-library/pull/226
- 2026-11-10 Design changed: was the Open item "Does the user want the usability audits to require `commit`", now settled in Design as required, because the user chose it
- 2026-11-10 PR: #227 https://github.com/cheneeheng/ceh-claude-code-library/pull/227
- 2026-11-10 Design changed: was "`within_noise` is false on the baseline, and `kept_commit` is required exactly when `kept` is true", now also refuses a kept baseline and a baseline median of 0 or less, because a kept baseline has no win to name and a zero median has no percent change for the renderer to compute
- 2026-11-10 Built Phase 1: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-10 PR: #228 https://github.com/cheneeheng/ceh-claude-code-library/pull/228
- 2026-11-10 Built Phase 2: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-10 PR: #230 https://github.com/cheneeheng/ceh-claude-code-library/pull/230
- 2026-11-10 Built Phase 3: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-10 PR: #231 https://github.com/cheneeheng/ceh-claude-code-library/pull/231
- 2026-11-10 Built Phase 4: Built by `product/plans/fix-record-yaml.yaml`, `python tools/validate-plugins/validate.py`,
  "OK: all plugin checks passed"
- 2026-11-10 PR: #238 https://github.com/cheneeheng/ceh-claude-code-library/pull/238
- 2026-11-10 Built Phase 5: Built by `product/plans/handoff-yaml.yaml`, `python tools/validate-plugins/validate.py`, "OK:
  all plugin checks passed"
- 2026-11-10 PR: #240 https://github.com/cheneeheng/ceh-claude-code-library/pull/240
- 2026-11-10 PR: #242 https://github.com/cheneeheng/ceh-claude-code-library/pull/242
- 2026-11-11 Design changed: Phase 6 was unplanned with its Check deferred until Phases 1 to 3 were judged. It now names
  all six child plans, has a Check requiring their builds and recorded evidence, and is todo.
  The three new plans cover glossary, blog voice and repeat-mistake reports. No new format
  implementation is claimed by this planning update.
- 2026-11-11 Design changed: Retained the original Phase 6 planning-only Builds after independent review, replacing
  the interim child-build Check with six plan validations and reviews. All six checks passed,
  but the completion record was blocked by the installed guard. The phase remains todo,
  the parent building, and the three new child plans ready with their implementation todo.
- 2026-11-11 PR: #254 https://github.com/cheneeheng/ceh-claude-code-library/pull/254
- 2026-11-11 Reviewed: Phase 6 only: Ready to build, 0 blocking, 2 advisory (the guard failure keeping Phase 6
  todo has no fix record; two overlapping Design changed records).
  Review: .agents_workspace/product/plan-reviews/report-only-formats-2026-11-11.md.

<!-- prettier-ignore-end -->
