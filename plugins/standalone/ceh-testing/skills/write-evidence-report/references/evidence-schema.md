# Evidence schema

The `.agents_workspace/product/EVIDENCE.yaml` that `write-evidence-report` keeps, with its Markdown
rendered beside it, unless the repo's `CLAUDE.md` names another location. A reference to it names
the `.yaml`. The `v1` layout below is what the Markdown keeps. A `v1` file is a copy of
`../assets/evidence.template.md`, relative to this file. The `schema: evidence/v1` line stays as
written. A file without it gets the template's frontmatter on the next run, and its sections stay
as they are.

## Frontmatter

- `product`: the product the evidence is for.

## Run sections

Each run adds one `## YYYY-MM-DD at <short-sha>` section below the title, newest first. Earlier
sections are never edited: each one is what was proven at its commit, and a plan's Record cites it
by date.

- **Tree:** `clean`, or `dirty (<n> files)`.
- **Area table:** one row per area, in the template's order.
  - **Status:** Tests is `passed`, `failed`, or `not run`. The other areas are `passed`,
    `open issues`, `stale (<n>)` (the report is `<n>` commits behind), or `not run`.
  - **Result:** the figure copied from the area's report or this session's test run, never
    estimated: the test command and its summary line, the QA bugs found and fixed, the metric and
    its value on its machine, the security counts by severity, the usability blocker and friction
    counts, or the plan items built and missing.
  - **Checked at:** the SHA, or the date when the report gives no SHA.
- **Open issues:** one bullet per issue, with its area and its severity where the report gives
  one: critical and high security findings, confirmed QA bugs not yet fixed, usability blockers,
  and plan items missing or failing their check. `None` when empty.
- **Claims:** one sentence each that a launch post may state, with its area and figure.
- **Not run:** each area not run, with the reason and the skill that produces it.

## evidence/v2: YAML with generated Markdown

An `evidence/v2` report is `.agents_workspace/product/EVIDENCE.yaml`, a copy of
`../assets/evidence.template.yaml`, and its Markdown is generated from it in the `v1` layout above
and saved beside it.
The YAML is the source: agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: EVIDENCE.yaml` and a do-not-edit `generated_note`. The format in code is
`evidence-model.py` beside this file, and `scripts/artifact.py` in the skill checks and renders it
through uv:

```bash
uv run --script scripts/artifact.py check .agents_workspace/product/EVIDENCE.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render .agents_workspace/product/EVIDENCE.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `runs.0` is the
newest run.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `evidence/v2`. `product`: as in `v1`.
- `runs`: at least one, newest first, each with `date` (an unquoted date), `sha` (7 to 40 lowercase
  hex characters), `tree` (`clean` or `dirty (<n> files)`), `areas`, `open_issues`, `claims` and
  `not_run`. A run is appended at the top, and an earlier run is never edited.
- `areas`: the six keys `tests`, `qa`, `performance`, `security`, `usability`, `plan`, each with
  `status`, `result` and `checked_at`. Tests `status` is `passed`, `failed` or `not run`, the others
  `passed`, `open issues`, `stale (<n>)` or `not run`. `result` and `checked_at` may be left out
  only when the status is `not run`, and every `not run` area has a `not_run` entry.
- `open_issues`: `area`, `issue` and `severity` (optional). `claims`: `claim`, `area`, `figure`.
  `not_run`: `area`, `reason`, `skill`. Each `area` is one of the six keys, and the Markdown shows
  its display name. An empty list is `[]` and renders as `None`.

**Free text goes in `|` blocks or quotes**, because ` #` starts a YAML comment, and every value is
strict, so quote a value such as `1.10` that must stay text.

A `v1` `EVIDENCE.md` with no YAML beside it is moved on the next run: write `EVIDENCE.yaml` from
it, every earlier section as a run, render, and check `git diff --no-index --word-diff` between a
copy of the old Markdown and the rendered one before adding the new run. Text the YAML cannot hold goes in the nearest free-text field, and the
reply names the move and any line the diff shows changed.
