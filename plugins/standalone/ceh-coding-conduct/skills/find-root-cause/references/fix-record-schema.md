# Fix record schema

Every bug fix leaves a record, `.agents_workspace/product/fix/<YYYYMMDD-HHMMSS>-<slug>.yaml` in
the target repo (`fix-record/v3`, below) with its `.md` generated beside it, unless the repo's
`CLAUDE.md` names another location. A reference to it names the `.yaml`. The time is the record's
creation, from one `date +%Y%m%d-%H%M%S` call, and never changes on later edits. It carries no
session id, because several sessions edit a record in place. A record saved before 2026-11-17 is
`<slug>.yaml` (`fix-record/v2`) or a `<slug>.md` with no YAML beside it (`fix-record/v1`), and
keeps its name and contents. A workspace not yet migrated keeps its records in the older
`.agents_workspace/product/fixes/`: a skill that looks for a record also looks there, and saves a
new one only to `fix/`. The commit message is written for reviewers of one change and the
diagnosis in the chat ends with the session, so the record is the only place a later session or
person finds why the fix exists.

**One record covers one functionality**: a change that lands in its own PR and can be checked on
its own. `<slug>` is kebab-case and names that functionality (`duration-parsing`), never a ticket
number. A record holds every issue found in its functionality until its fix lands, each issue
being one behavior that was wrong. Two issues with one root cause in two functionalities go in the
record of the functionality that owns the cause, and the other record's issue names it in its
cause.

**Write one only when the cause is in this repo's code or config**, because that is what a later
reader of the repo can act on. A cause on one machine, or a question nobody means to fix in code
("why is CI slow"), writes nothing, so `.agents_workspace/product/` does not fill with debugging
chats.

## Finding the record of a functionality

A record's slug is its file stem with any leading `YYYYMMDD-HHMMSS-` removed. A skill matches names
in the fix folder against `^(\d{8}-\d{6}-)?<slug>\.yaml$`, newest by time prefix first, so the slug
`parsing` never matches `duration-parsing`, and judges by `title` only when no slug matches.

- **Open**: a record whose `status` is `diagnosed`. A new issue in its functionality is added to
  its `issues`.
- **Closed**: any other status. It never takes a new issue. A later bug in that functionality gets
  a new record whose `previous:` names the closed one, so one record covers one landing and the
  landed record stays as it was.

## Fields

- **`status:`** the record's status, derived from its issues: `diagnosed` while any issue is,
  else `fixed` when any is, else `declined` when any is, else `unreproduced`.
- **`date:`** the date the record was first saved.
- **`issue:`** the link or ID of the report. Omit the key when there is none.
- **`plan:`** Grep the `status: built` plans in `.agents_workspace/product/plan/` for the file at
  a Cause's `file:line`, or at the fixed `file:line` when the record is created at fix time. With
  several matches, take the newest by the time prefix. No match, or a tie, leaves the field out:
  never guessed.
- **`previous:`** The closed record of the same functionality, so a bug that came back shows its
  history. Omit the key when no earlier record covers this functionality.
- **Title:** the functionality, in one line.
- **Issues:** one per behavior that was wrong, each with:
  - **Title:** the behavior that was wrong, in one line.
  - **Status:** `diagnosed` (cause found, fix to land here), `fixed`, `unreproduced`, or
    `declined` (the fix lands outside this repo, or the user declined it).
  - **Symptom:** the command that fails and its failing output line.
  - **Diagnosis table:** one row per hypothesis: the claim, the observation that would kill it,
    and whether it was refuted or confirmed, with the output that decided it.
  - **Cause:** the `file:line` or condition, then one sentence on the chain from cause to symptom.
  - **Prediction:** a command, and the result predicted and then seen.
  - **Fix:** one or two sentences: what changed and why that removes the cause.
  - **Tests:** one bullet per test: `protects` names the behavior, `fails_when` the defect
    returning, `why_new` why no existing test caught it.
  - **Unverified:** what stayed unrun and why, or `none`.

## Sections by status, per issue

- **`diagnosed`**: Symptom, Diagnosis and Cause, and no Fix yet.
- **`declined`**: Symptom, Diagnosis and Cause, where the Cause names where the fix belongs (the
  package and version, or the setting) or why the user declined it, and no Fix.
- **`fixed`**: all sections. When the cause was known from the report and no investigation ran,
  Diagnosis holds `Cause known from the report: <cause>` instead of the table.
- **`unreproduced`**: the Symptom names the reported failure, Diagnosis lists each attempt and what
  it showed, and there is no Cause or Fix.

## Rules

- **An issue's status moves forward only.** `diagnosed` to `fixed` or `declined`. `fixed`,
  `declined` and `unreproduced` are final. The PR that lands the fix sets each issue it fixed to
  `fixed`.
- **`Refs:` footer.** The record does not ride in the fix's commit. The fix's commit message
  carries the footer `Refs: fix/<stem>`, the record's whole file stem, so
  `git log -E --grep "fix(es)?/<stem>"` in the source repo finds the fix, also under the older
  `Refs: fixes/<slug>`. The record carries no commit SHA, because it is written before the commit
  exists. A record with no fix (every issue `unreproduced` or `declined`) is saved alone, so the
  investigation is not lost.
- **Only what ran.** Each Result and the Prediction quote output that a command produced. A
  conclusion from reading code is labelled inferred.

## fix-record/v3: YAML with generated Markdown

A `fix-record/v3` record is a copy of `../assets/fix-record.template.yaml`, and the `.md` of the
same name is generated from it in the layout of `../assets/fix-record.template.md`, beside it.
The YAML is the source: agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`. A `v2` or `v1` record stays as
written, and a `v2` record reports unchecked (exit 3), because the model is `v3` only. The format
in code is `fix-record-model.py` beside this file, and `scripts/artifact.py` in the skill checks
and renders it through uv:

```bash
uv run --script scripts/artifact.py check .agents_workspace/product/fix/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render .agents_workspace/product/fix/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so
`issues.0.diagnosis.rows.0` is the first issue's first hypothesis.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `fix-record/v3`. `status`: `diagnosed`, `fixed`, `unreproduced` or `declined`, and
  equal to the status the issues derive. `date`: an unquoted date. `issue` (optional): the report.
  `plan` (optional): a path starting `.agents_workspace/product/plan/`. `previous` (optional):
  the earlier record's path under `.agents_workspace/product/fix/`, its `.yaml` for a `v2` or `v3`
  record and its `.md` for a `v1` record. A path saved before 2026-11-14, starting at the old root,
  still checks.
- `title`: the functionality.
- `issues`: at least one, each with these keys:
  - `title`: the behavior that was wrong. `status`: as above.
  - `symptom`: `command` (optional) and `output`, the failing output line. With no command, as in
    an `unreproduced` issue, `output` is the reported failure.
  - `diagnosis`: exactly one of `rows` and `known_from_report`. `rows`: at least one, each with
    `hypothesis`, `refuted_by`, `result` (`refuted`, `standing` or `confirmed`) and `output`. In an
    `unreproduced` issue each attempt is a row whose hypothesis reads "it reproduces under
    <condition>". `known_from_report`: where the report names the cause, such as `issue #12`,
    rendered as `Cause known from the report: <it>` in place of the table.
  - `cause` (optional): `location`, the `file:line` or condition, or where the fix belongs when it
    lands elsewhere, and `chain`, cause to symptom.
  - `prediction`: a list, `[]` when none, each with `command` (optional) and `result`, the result
    predicted and then seen, one sentence each.
  - `fix` (optional): what changed and why. `tests`: a list, `[]` when none, each with `test`,
    `protects`, `fails_when` and `why_new`.
  - `unverified`: what stayed unrun, or `none`.

**Rules the model enforces**, the Sections by status above, per issue:

- `diagnosed` and `declined`: a `cause`, no `fix`, `tests: []`, and with `rows`, at least one
  `confirmed`.
- `fixed`: a `cause`, a `fix` and at least one test, and with `rows`, at least one `confirmed`.
  Only a `fixed` issue may use `known_from_report`.
- `unreproduced`: `rows` with none `confirmed`, no `cause` or `fix`, and `prediction: []` and
  `tests: []`.
- The record's `status` equals the one its issues derive.
- Each issue's `title`, both `symptom` keys, every `rows` key, `cause.location`, each `prediction`
  key and each test's four keys are one line, so the table cells and bullets render whole. A `|`
  in a table cell is escaped by the renderer.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.
