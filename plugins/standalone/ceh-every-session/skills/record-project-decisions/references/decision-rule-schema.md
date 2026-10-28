# Decision rule schema

One file per decision that `record-project-decisions` writes, `.claude/rules/decision-<topic>.md`.
A new file is a copy of `../assets/decision-rule.template.md`, relative to this file. The
`schema: decision-rule/v1` line stays as written.

## Frontmatter

- **`schema`:** `decision-rule/v1`, as written.
- **`paths`:** optional, a list of globs. Set it only when the decision concerns one part of the
  tree, and Claude Code then loads the file once a matching file is read instead of at launch.

## Body

- **Title:** the topic, not the answer, matching the file name.
- **Rule:** one or two imperative sentences.
- **Why line:** one line on the reason, the date decided, and the source: a path, `conversation`,
  or `<file> (<short commit hash>)` for a decision moved out of an existing file such as
  `CLAUDE.md`, naming the commit that first added it there.
