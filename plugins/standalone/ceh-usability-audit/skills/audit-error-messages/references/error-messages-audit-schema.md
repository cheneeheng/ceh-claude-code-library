# Error messages audit schema

The report `audit-error-messages` writes to
`.agents_workspace/ux-audits/<target>/run-<NNN>/ERROR_MESSAGES.md`, with a zero-padded run index so a
re-run never overwrites the previous evidence. A new report is a copy of
`../assets/error-messages-audit.template.md`, relative to this file. The
`schema: error-messages-audit/v1` line stays as written.

## Frontmatter

- `target`: the product or codebase audited.
- `run`: the zero-padded run index, matching the folder.
- `date`: the run date.
- `harvested`: the number of messages harvested.
- `already_complete`: how many satisfied all three parts before any rewrite. This is the number
  that moves when a codebase gets better.

## Body

- **Counts:** the same two numbers as the frontmatter, at the top, because they tell whether the
  next pass is worth running.
- **Triage:** one row per message. Location is the `path:line`, and Current text the message as
  found. Columns 1, 2, and 3 are the skill's three parts, each `✓` or `✗`. Severity is `Blocker`,
  `Detour`, `Friction`, or `Polish`. Rewrite is the new text. Applied is `yes`, or `no` with the
  reason it was left.
- **Systemic causes:** each shared handler or wrapper behind several `✗` rows, and whether it was
  fixed once.
