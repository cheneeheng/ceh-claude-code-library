# Handoff schema

The file `hand-off-session` saves to
`.agents_workspace/handoff/<YYYYMMDD-HHMMSS>-<session-id>-handoff.yaml` (`handoff/v2`, below), with
the `.md` rendered beside it, or to the `.yaml` of the stem a caller passes with
`save --file <path>`, overwritten on each save, and `load` reads back. A reference to it names the
`.yaml`. A
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

## handoff/v2: YAML with generated Markdown

A `handoff/v2` handoff is `<YYYYMMDD-HHMMSS>-<session-id>-handoff.yaml`, a copy of
`../assets/handoff.template.yaml`, and the `.md` of the same stem is generated from it in the `v1`
layout above, beside it. With `save --file <path>`, the YAML is `<path>` with its suffix replaced
by `.yaml`, and the Markdown keeps the path the caller named. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. A `v1` `.md` with no `.yaml` beside it is still read as `v1`. The
format in code is `handoff-model.py` beside this file, and `scripts/artifact.py` in the skill
checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `open.0` is the
next step.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `handoff/v2`. `saved`: `YYYY-MM-DD HH:MM`, quoted. `session`: the 8-character session
  id prefix.
- `header`: a caller's header lines, rendered under the title. `repo`: the working directory.
  `branch`: the branch, or `no git`.
- `fields`: the caller fields, each `name` and `value`, in the order the caller named them.
- `goal`: at least one line. `done`: each `item`, `files` (`none` when no file was touched) and
  `validated` (`true` or `false`). `in_flight`: the state of anything closed or reverted.
- `open`: at least one item, the first the next actionable step. When the work is finished, the
  item is the check that confirms it or the next task the user named, never a made-up step.
- `decisions_pending`: each fork, `[]` when none. `forks_go_to` (optional): the place a caller
  named for decisions, rendered `, forks go to <place>`.
- `resume_with`: one line.

Every value and list item is one line. An empty list is `[]`: an empty `done` or `in_flight`
renders as `- none`, and an empty `decisions_pending` as `none`.

**Quoting:** single-quote any value that starts with `*`, contains `: ` or ` #`, or holds a
backslash, such as `'**Window:** 5h at 92%, resets at 14:00'`, `'Which DB: postgres or sqlite'`,
`'Opened PR #12'` or `'D:\work\proj'`. YAML reads a leading `*` as an alias, `: ` as a key,
` #` as a comment, and a backslash in double quotes as an escape. Every value is strict, so quote
a value such as `1.10` that must stay text.
