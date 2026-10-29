# Decision rule schema

One file per decision that `record-project-decisions` writes, `decision-<topic>.md`, in
`.claude/rules/` for a project decision or `~/.claude/rules/` for a user decision. A new file is a
copy of `../assets/decision-rule.template.md`, relative to this file. The
`schema: decision-rule/v2` line stays as written.

## Frontmatter

Claude Code reads only `paths` and strips the frontmatter before loading the rule, so the other
fields serve a human tracing the decision and cost no context.

- **`schema`:** `decision-rule/v2`, as written.
- **`decided`:** the date decided, `YYYY-MM-DD`. When the decision was changed later, the latest
  date: `git log` on the file keeps the earlier ones.
- **`source`:** always quoted, because sources hold `: ` and backticks, and single-quoted when the
  value holds a double quote. A path,
  `conversation`, or `<file> (<short commit hash>)` for a decision moved out of an existing file
  such as `CLAUDE.md`, naming the commit that first added it there.
- **`paths`:** optional, after `source`, a list of globs. Set it only when the decision concerns
  one part of the tree, and Claude Code then loads the file once a matching file is read instead of
  at launch.

## Body

- **Title:** the topic, not the answer, matching the file name.
- **Rule:** one or two imperative sentences.
- **Why line:** one line on the reason, with no date or source.

## Versions

- **v2:** `decided` and `source` moved from the Why line into frontmatter. A v1 file is migrated
  when it is next edited.
