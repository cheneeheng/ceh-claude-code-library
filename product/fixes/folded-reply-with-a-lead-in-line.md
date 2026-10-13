---
status: fixed
date: 2026-10-13
previous: folded-topic-keeps-its-whole-body.md
---

# A reply with a sentence before its summary table is not folded

**Symptom:** A reply that opens with one sentence and then the summary table draws whole, with no
Topic boxes and no folds, although every Topic below the table is well formed.

## Diagnosis

| Hypothesis                                           | Refuted by                                         | Result                                                                                                                                                                                    |
| ---------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The parser needs the table on the reply's first line | A reply with a lead-in sentence folding its Topics | confirmed: against the old parser, `claude plugin test .` fails `a lead-in line before the summary table shows as is, and the topics still fold`, the mod handing the reply to the engine |

**Cause:** `plugins/standalone/ceh-every-session/hooks/split-summary.ts`: `split` returned null
unless the first line was a table row and the second its separator. The output style forbids text
before the table, but the model sometimes writes a sentence there, and the whole reply then lost
its folds.

**Prediction:** `claude plugin test .` against the fixed parser → 11 pass, 0 fail.

## Fix

`split` finds the first table and keeps one paragraph before it as `lead`, drawn as is above the
table. Two or more paragraphs before the table still return null, so a prose reply with a table
further down draws whole.

**Tests:**

- `a lead-in line before the summary table shows as is, and the topics still fold` — protects: a
  one-paragraph lead-in keeps the folds; fails_when: `split` requires the table on line one;
  why_new: every earlier test opened with the table.
- `a reply with two paragraphs before its first table is drawn whole by the engine` — protects: a
  prose reply is not folded; fails_when: any text before a table counts as a lead-in; why_new: the
  lead-in rule needs a limit.

**Unverified:** I did not check rendering in a live session, only the mod's test harness.
