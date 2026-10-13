---
status: fixed
date: 2026-10-13
---

# A folded Topic drops its tables, code, and later paragraphs outside the fold

**Symptom:** A reply whose Topic holds a paragraph, a table, or a code block followed by more text
draws only the first run of bullets or the first paragraph inside the fold. The rest prints below
the box, outside any Topic.

## Diagnosis

| Hypothesis                                               | Refuted by                                                  | Result                                                                                                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| The parser ends a Topic's body at the first shape change | A Topic of bullets, a table, and more bullets folding whole | confirmed: against the old parser, `claude plugin test .` fails `paragraphs, tables, and bullets after them all stay inside their fold` |

**Cause:** `plugins/standalone/ceh-every-session/hooks/split-summary.ts`: the parser guessed a
body's end from its shape, one run of bullets or one paragraph, so it could tell closing text
apart from the last Topic. Any first line past that shape, such as a table row or a second
paragraph, ended the body, and every line up to the next Topic went to `after`.

**Prediction:** `claude plugin test .` against the fixed parser → 9 pass, 0 fail.

## Fix

A Topic's body now runs to the next bold Topic, and closing text sits below a `---` line, which
the output style now requires. No shape guess remains, so whatever the model writes under a Topic
folds with it.

**Tests:**

- `paragraphs, tables, and bullets after them all stay inside their fold` — protects: a Topic with
  bullets, a paragraph, a table, and more bullets folds whole; fails_when: the body ends before the
  next Topic; why_new: the earlier tests held only bullets and code blocks.
- `closing text below a --- line shows as is, outside its fold` — protects: closing text stays
  outside the last fold; fails_when: the `---` marker is not honoured; why_new: replaces the test of
  the removed shape guess.

**Unverified:** I did not check rendering in a live session, only the mod's test harness. A model
reply that leaves out the `---` line folds its closing text into the last Topic.
