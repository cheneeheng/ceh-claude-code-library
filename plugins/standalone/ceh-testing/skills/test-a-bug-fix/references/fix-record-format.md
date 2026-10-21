# Fix record format

Every bug fix leaves one committed file, `product/fixes/<slug>.md` in the target repo. The commit
message is written for reviewers of one change and the diagnosis in the chat ends with the session,
so the record is the only place a later session or person finds why the fix exists. `<slug>` is
kebab-case and names the behavior that was wrong, as the regression test does
(`parse-duration-accepts-bare-number`), never a ticket number. If the slug is taken, add `-2`.

**Write one only when the cause is in this repo's code or config**, because that is what a later
reader of the repo can act on. A cause on one machine, or a question nobody means to fix in code
("why is CI slow"), writes nothing, so `product/` does not fill with debugging chats.

## Format

A record is a copy of `fix-record.template.md`, next to this file, keeping only the sections its
status keeps (see Sections by status). The `schema: fix-record/v1` line stays as written.

## Fields

- **`plan:`** Grep the `status: built` plans in `product/plans/` for the file at the Cause's
  `file:line`, or at the fixed `file:line` when the record is created at fix time. With several
  matches, take the newest by `created:`. No match, or a tie on that date, leaves the field out:
  never guessed.
- **`previous:`** The earlier record in `product/fixes/` whose Cause matches the confirmed one, so a
  bug that came back shows its history.

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
