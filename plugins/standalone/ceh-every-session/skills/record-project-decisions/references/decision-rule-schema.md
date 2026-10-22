# Decision rule schema

One file per decision that `record-project-decisions` writes, `.claude/rules/decision-<topic>.md`.
A new file is a copy of `../assets/decision-rule.template.md`, relative to this file. The
`schema: decision-rule/v1` line stays as written.

## Body

- **Title:** the topic, not the answer, matching the file name.
- **Rule:** one or two imperative sentences.
- **Why line:** one line on the reason, the date decided, and the source: a path, or
  `conversation`.
