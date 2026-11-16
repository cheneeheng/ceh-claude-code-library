# Stress test schema

The file `stress-test-plan` saves to
`.agents_workspace/product/review/stress-test/<YYYYMMDD-HHMMSS>-<session-id>-<topic>.yaml`, with its
`.md` rendered beside it, when there is no plan file to write the outcome back to. A reference to
it names the `.yaml`. Its layout is `../assets/stress-test.template.md`, relative to this file. A
new file is written as `stress-test/v2` YAML, per the section at the end, and an older
`stress-test/v1` file, a `.md` with no YAML beside it, stays as written, its `schema:` line
included.

## Frontmatter

- `date`: the session date.
- `topic`: the plan's topic, matching the file name.

## Body

- **Plan:** a one-line statement of the plan, above the sections.
- **Decisions:** each settled question, with its answer and a one-line reason.
- **Open:** each question left, with the recommendation assumed and `not confirmed`, or
  `blocked on <prerequisite>` when it waits on another answer.

## stress-test/v2: YAML with generated Markdown

A `stress-test/v2` file is a copy of `../assets/stress-test.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. The format in code is `stress-test-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `open.0` is the
first open question.

**Keys**, each required, and no other key allowed:

- `schema`: `stress-test/v2`. `date`: an unquoted date. `topic`: lowercase words joined by
  hyphens, as in the file name.
- `plan`: the plan statement, in a `|` block.
- `decisions`: `question`, `answer` and `reason`, each one line.
- `open`: `question`, `state` and `detail`, each one line. `state: assumed` takes the
  recommendation as `detail` and renders `assumed <detail>, not confirmed`. `state: blocked` takes
  the prerequisite and renders `blocked on <detail>`. With no human to answer, list the assumed
  ones first.
- An empty list is `[]` and renders as `None`.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote**, because YAML reads
` #` as a comment.
