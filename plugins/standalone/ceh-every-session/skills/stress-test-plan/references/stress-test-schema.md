# Stress test schema

The file `stress-test-plan` saves to
`.agents_workspace/product/review/stress-test/<YYYYMMDD-HHMMSS>-<topic>.yaml`, with its `.md`
rendered beside it, when there is no plan file to write the outcome back to, one file per topic,
updated in place by every later stress test of that topic. A reference to it names the `.yaml`.
Its layout is `../assets/stress-test.template.md`, relative to this file. A new file is written as
`stress-test/v2` YAML, per the section at the end, and an older `stress-test/v1` file, a `.md`
with no YAML beside it, stays as written, its `schema:` line included.

## Review lifecycle

Every saved review follows these rules, whatever its kind. The section is copied word for word
into each review format's schema, and only the Targets line differs.

- **Name:** `.agents_workspace/product/review/<kind>/<YYYYMMDD-HHMMSS>-<target>.yaml`, the time
  from one `date +%Y%m%d-%H%M%S` call when the file is first saved, never changed after. It
  carries no session id, because several sessions edit a review in place.
- **Lookup:** match names in the kind's folder against
  `^\d{8}-\d{6}-([0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}-)?<target>\.yaml$`, so an older name
  with a session id counts and `layout` never matches `workspace-layout`, and take the newest by
  time prefix. With none, save a new file. Older duplicates are left as written.
- **Convert:** a found file of the kind's older YAML version is rewritten in place to the new one,
  its content becoming round 1 and each of its findings `open`, keeping its name.
- **Cold round:** the reviewer reads the target before the review file, and a subagent reviewer
  gets the target and never the file, so earlier rounds cannot anchor it.
- **Re-check:** before a round is merged, each `open` finding is read against the current target
  and set `fixed`, with the resolution `found fixed in round <n>`, where the target no longer has
  the defect.
- **Merge:** a finding that repeats an `open` one is not added again, and one that repeats a
  `fixed` one reopens it with a note in its resolution.
- **Tick off:** the session that makes a fix sets the finding's status and resolution (the edit,
  commit or PR, or why it will not be fixed) when it knows of the review file.
- **Targets:** a stress test's target is its topic, and its findings are its `open` list: an
  answered question moves to `decisions`, which is how it is ticked off.

## Updating a topic's file

A later stress test of the same topic, run without a plan file, updates the file it finds:

- It adds each newly settled question to `decisions`.
- It changes a decision only when the user answers it differently, with the reason saying what
  changed.
- It moves a question from `open` to `decisions` once answered, and adds new open questions.
- It sets `date` to the run's date. The file keeps its name.

## Frontmatter

- `date`: the date of the latest run on the topic.
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
