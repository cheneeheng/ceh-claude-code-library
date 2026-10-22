# Stress test schema

The file `stress-test-plan` saves to `.agents_workspace/stress-tests/<YYYY-MM-DD>-<topic>.md` when
there is no plan file to write the outcome back to. A new file is a copy of
`../assets/stress-test.template.md`, relative to this file. The `schema: stress-test/v1` line stays
as written.

## Frontmatter

- `date`: the session date.
- `topic`: the plan's topic, matching the file name.

## Body

- **Plan:** a one-line statement of the plan, above the sections.
- **Decisions:** each settled question, with its answer and a one-line reason.
- **Open:** each question left, with the recommendation assumed and `not confirmed`, or
  `blocked on <prerequisite>` when it waits on another answer.
