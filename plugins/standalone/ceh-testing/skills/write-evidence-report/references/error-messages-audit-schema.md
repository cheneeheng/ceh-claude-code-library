# Error messages audit schema

The report `audit-error-messages` writes to
`.agents_workspace/product/ux-audits/<target>/run-<NNN>/ERROR_MESSAGES.md`, with a zero-padded run index so a
re-run never overwrites the previous evidence. Its layout is
`../assets/error-messages-audit.template.md`, relative to this file. A new report is written as
`error-messages-audit/v2` YAML, per the section at the end, and an older `error-messages-audit/v1`
report stays as written, its `schema:` line included.

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

## error-messages-audit/v2: YAML with generated Markdown

An `error-messages-audit/v2` report is `ERROR_MESSAGES.yaml`, a copy of
`../assets/error-messages-audit.template.yaml`, and `ERROR_MESSAGES.md` is generated from it in the
`v1` layout above, beside it. The YAML is the source: agents read and edit it, and nobody edits the
Markdown, which opens with `generated_from: ERROR_MESSAGES.yaml` and a do-not-edit
`generated_note`. The format in code is `error-messages-audit-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/ERROR_MESSAGES.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/ERROR_MESSAGES.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `rows.0` is row 1.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `error-messages-audit/v2`. `target`: as in `v1`. `run`: an int, rendered zero-padded to
  three digits (`007`) to match the `run-<NNN>` folder. `date`: an unquoted date.
- `commit`: the target's commit as audited, 7 to 40 lowercase hex characters, never a name such as
  `HEAD`, because `write-evidence-report` runs `git log <commit>..HEAD` on it.
- `harvested` and `already_complete`: ints, with `already_complete <= harvested`.
- `rows`: `location`, `current`, `checks` (exactly three booleans, the skill's three parts, rendered
  `✓` or `✗`), `severity` (`Blocker`, `Detour`, `Friction` or `Polish`), `rewrite`, `applied`, and
  `reason` (optional), given exactly when `applied` is false. The renderer numbers the rows from 1.
- `systemic`: `handler`, `rows` (the row numbers it is behind, each a row in the file) and `fixed`.
  An empty list is `[]` and renders as `None`.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.
