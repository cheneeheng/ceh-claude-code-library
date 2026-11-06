# Handoff schema

The file `hand-off-session` saves to
`.agents_workspace/handoff/HANDOFF-<YYYYMMDD-HHMM>-<session-id-prefix>.md`, or to the path a
caller passes with `save --file <path>`, overwritten on each save, and `load` reads back. A
new handoff is a copy of `../assets/handoff.template.md`, relative to this file. The
`schema: handoff/v1` line stays as written.

## Frontmatter

- `saved`: the save time, from a single `date` call.
- `session`: the first 8 characters of the session id.

## Body

- **Title:** `Handoff — ` and the save time. A caller's own header lines (a usage window, a reason)
  go directly under it.
- **Repo / branch:** the working directory, and the branch or `no git`.
- **Session:** the same session id prefix as the frontmatter.
- **Caller fields:** optional, one `**<Field>:** <value>` line each, directly after Session, in
  the order the caller named them. Load reports them. A reader that ignores them loses nothing, so
  the schema stays `handoff/v1`.
- **Goal:** what this session set out to do, in one or two lines.
- **Done:** each item completed, with the files touched and whether it was validated.
- **In flight:** the step closed or reverted at the save: the state of the working tree, anything
  half-planned.
- **Open:** the remaining work, ordered. The first item is the next actionable step, specific
  enough to execute cold.
- **Decisions pending:** forks the user still has to resolve, or `none`. When the caller names a
  place for decisions, the line ends `, forks go to <place>`, and load sends each blocking fork
  there instead of to the user.
- **Resume with:** one line: the branch name, the command to run, or the file to open first.
