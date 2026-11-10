# QA report schema

The report `explore-app-for-bugs` writes to `.agents_workspace/product/qa/<YYYYMMDD-HHMM>/QA_REPORT.md`,
with screenshots and logs beside it. Its layout is `../assets/qa-report.template.md`, relative to
this file. A new report is written as `qa-report/v2` YAML, per the section at the end, and an
older `qa-report/v1` report stays as written, its `schema:` line included.

## Frontmatter

- `app`: the app explored.
- `commit`: the commit it ran at.
- `mode`: `report` or `fix`.
- `date`: the run time, from one `date` call.

## Body

- **Launched with:** the documented launch command and the URL or entry point it opened.
- **Mode:** the same mode as the frontmatter.
- **Charters:** one row per charter, `Explore <area> with <technique> to find <risk>`, the actions
  used out of 20, and the IDs of the bugs it found.
- **Bugs:** one `### <ID>: <severity>: <one-line title>` per bug. Severity is `Critical`, `Major`,
  `Minor`, or `Cosmetic`, per the skill's scale.
  - **Status:** `confirmed (reproduced twice)` or `unconfirmed`.
  - **Steps:** numbered, enough to reproduce.
  - **Expected / actual:** what should happen, and what did.
  - **Evidence:** a screenshot path, a console line, or a response body.
  - **Fix:** fix mode only: the commit and the re-run result. Omit in report mode.
- **Usability notes (not bugs):** confusing wording, layout, or flow, kept apart from the bugs.
- **Not explored:** the flows, roles, or environments no charter covered, and why.

## qa-report/v2: YAML with generated Markdown

A `qa-report/v2` report is `QA_REPORT.yaml`, a copy of `../assets/qa-report.template.yaml`, and
`QA_REPORT.md` is generated from it in the `v1` layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: QA_REPORT.yaml` and a do-not-edit `generated_note`. The format in code is
`qa-report-model.py` beside this file, and `scripts/artifact.py` in the skill checks and renders it
through uv:

```bash
uv run --script scripts/artifact.py check <dir>/QA_REPORT.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/QA_REPORT.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `charters.0` is the
first charter.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `qa-report/v2`. `app`, `mode` (`report` or `fix`) and `date` (`YYYY-MM-DD HH:MM`): as
  in `v1`. `commit`: 7 to 40 lowercase hex characters, never a name such as `HEAD`, because
  `write-evidence-report` runs `git log <commit>..HEAD` on it.
- `launched_with`: `command` and `entry`, the URL or entry point it opened.
- `charters`: `charter`, `actions_used` (0 to 20) and `bugs`, the IDs it found. Every ID a charter
  names is a bug in the file.
- `bugs`: `id` (unique), `severity` (`Critical`, `Major`, `Minor` or `Cosmetic`), `title`, `status`
  (`confirmed` or `unconfirmed`, rendered `confirmed (reproduced twice)` for the first), `steps`
  (at least one, numbered by the renderer), `expected`, `actual`, `evidence`, and `fix` (optional,
  `commit` and `rerun`), allowed only when `mode` is `fix`.
- `usability_notes`: one string each. `not_explored`: `what` and `why`. An empty list is `[]` and
  renders as `None`.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.
