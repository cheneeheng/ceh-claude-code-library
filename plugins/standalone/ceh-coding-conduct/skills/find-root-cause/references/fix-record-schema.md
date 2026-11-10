# Fix record schema

Every bug fix leaves one committed record, `product/fixes/<slug>.md` in the target repo, or for
`fix-record/v2` (below) `product/fixes/<slug>.yaml` with that `.md` generated beside it. The commit
message is written for reviewers of one change and the diagnosis in the chat ends with the session,
so the record is the only place a later session or person finds why the fix exists. `<slug>` is
kebab-case and names the behavior that was wrong, as the regression test does
(`parse-duration-accepts-bare-number`), never a ticket number. If the slug is taken, add `-2`.

**Write one only when the cause is in this repo's code or config**, because that is what a later
reader of the repo can act on. A cause on one machine, or a question nobody means to fix in code
("why is CI slow"), writes nothing, so `product/` does not fill with debugging chats.

## Format

A record is a copy of `../assets/fix-record.template.md`, relative to this file, keeping only the
sections its status keeps (see Sections by status). The `schema: fix-record/v1` line stays as
written.

## Fields

- **`status:`** `diagnosed`, `fixed`, or `unreproduced`, per Sections by status.
- **`issue:`** the link or ID of the report. Omit the key when there is none.
- **Title:** the behavior that was wrong, in one line.
- **Symptom:** the command that fails and its failing output line.
- **Diagnosis table:** one row per hypothesis: the claim, the observation that would kill it, and
  whether it was refuted or confirmed, with the output that decided it.
- **Cause:** the `file:line` or condition, then one sentence on the chain from cause to symptom.
- **Prediction:** a command, and the result predicted and then seen.
- **Fix:** one or two sentences: what changed and why that removes the cause.
- **Tests:** one bullet per test: `protects` names the behavior, `fails_when` the defect
  returning, `why_new` why no existing test caught it.
- **Unverified:** what stayed unrun and why, or `none`.
- **`plan:`** Grep the `status: built` plans in `product/plans/` for the file at the Cause's
  `file:line`, or at the fixed `file:line` when the record is created at fix time. With several
  matches, take the newest by `created:`. No match, or a tie on that date, leaves the field out:
  never guessed.
- **`previous:`** The earlier record in `product/fixes/` whose Cause matches the confirmed one, so a
  bug that came back shows its history. Omit the key when no earlier record covers this behavior.

## Sections by status

- **`diagnosed`**: Symptom and Diagnosis. When the fix will not land in this repo (the cause is in
  a dependency or the environment, or the fix is declined), the record keeps no Fix section and its
  Cause names where the fix belongs: the package and version, or the setting.
- **`fixed`**: all three sections. When the cause was known from the report and no investigation
  ran, Diagnosis holds `Cause known from the report: <cause>` instead of the table.
- **`unreproduced`**: the Symptom names the reported failure, Diagnosis lists each attempt and what
  it showed, and there is no Fix section.

## Rules

- **`status` moves forward only.** `diagnosed` to `fixed`. `unreproduced` is final, and so is a
  `diagnosed` record whose fix never lands here. A later fix to the same behavior gets a new record
  whose `previous:` names the old one, so the old record stays as it was.
- **Same commit.** The record, the fix, and the regression test land in one commit, so
  `git log -- product/fixes/<slug>.md` finds the fix. The record carries no commit SHA, because the
  commit cannot name its own. A record with no fix (`unreproduced`, or `diagnosed` with the fix
  elsewhere) is committed alone, so the investigation is not lost.
- **Only what ran.** Each Result and the Prediction quote output that a command produced. A
  conclusion from reading code is labelled inferred.

## fix-record/v2: YAML with generated Markdown

A `fix-record/v2` record is `product/fixes/<slug>.yaml`, a copy of
`../assets/fix-record.template.yaml`, and `product/fixes/<slug>.md` is generated from it in the
`v1` layout above, beside it. The YAML is the source: agents read and edit it, and nobody edits the
Markdown, which opens with `generated_from: <slug>.yaml` and a do-not-edit `generated_note`. The
Fields, Sections by status and Rules above still hold. A `v1` record with no `.yaml` beside it
stays Markdown and is completed in the `v1` form. The format in code is `fix-record-model.py`
beside this file, and `scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check product/fixes/<slug>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render product/fixes/<slug>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `diagnosis.rows.0`
is the first hypothesis.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `fix-record/v2`. `status`: `diagnosed`, `fixed` or `unreproduced`. `date`: an
  unquoted date. `issue` (optional): as in `v1`. `plan` (optional): a path starting
  `product/plans/`. `previous` (optional): the earlier record's `.md` path under `product/fixes/`,
  which exists for a `v1` and a `v2` record alike.
- `title`: the behavior that was wrong.
- `symptom`: `command` (optional) and `output`, the failing output line. With no command, as in an
  `unreproduced` record, `output` is the reported failure.
- `diagnosis`: exactly one of `rows` and `known_from_report`. `rows`: at least one, each with
  `hypothesis`, `refuted_by`, `result` (`refuted`, `standing` or `confirmed`) and `output`. In an
  `unreproduced` record each attempt is a row whose hypothesis reads "it reproduces under
  <condition>". `known_from_report`: where the report names the cause, such as `issue #12`,
  rendered as `Cause known from the report: <it>` in place of the table.
- `cause` (optional): `location`, the `file:line` or condition, or where the fix belongs when it
  lands elsewhere, and `chain`, cause to symptom.
- `prediction`: a list, `[]` when none, each with `command` (optional) and `result`, the result
  predicted and then seen, one sentence each.
- `fix` (optional): what changed and why. `tests`: a list, `[]` when none, each with `test`,
  `protects`, `fails_when` and `why_new`.
- `unverified`: what stayed unrun, or `none`.

**Rules the model enforces**, the Sections by status above:

- `diagnosed`: a `cause`, no `fix`, `tests: []`, and with `rows`, at least one `confirmed`.
- `fixed`: a `cause`, a `fix` and at least one test, and with `rows`, at least one `confirmed`.
  Only a `fixed` record may use `known_from_report`.
- `unreproduced`: `rows` with none `confirmed`, no `cause` or `fix`, and `prediction: []` and
  `tests: []`.
- `title`, both `symptom` keys, every `rows` key, `cause.location`, each `prediction` key and each
  test's four keys are one line, so the table cells and bullets render whole. A `|` in a table cell
  is escaped by the renderer.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.
