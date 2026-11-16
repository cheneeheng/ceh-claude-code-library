# Test audit schema

The report `audit-test-suite` saves to
`.agents_workspace/product/audit/test/<YYYYMMDD-HHMMSS>-<session-id>-test-audit.yaml`, with its
`.md` rendered beside it. A reference to it names the `.yaml`. A subagent in report-only mode
returns the YAML instead, and its caller saves and renders it. Its layout is
`../assets/test-audit.template.md`, relative to this file. A new report is written as
`test-audit/v2` YAML, per the section at the end, and an older `test-audit/v1` report, a `.md`
with no YAML beside it, stays as written, its `schema:` line included.

## Frontmatter

- `date`: the audit date.
- `commit`: the short SHA audited.
- `mode`: `fix` or `report-only`.

## Sections

- **Findings:** worst first, one line each: the severity, the `path:line` (or the module, for a
  mutation result), and the finding, quoting the code it is about. For example:

  ```
  CRITICAL  tests/unit/test_billing.py:41  no assertion — only checks no exception raised
  HIGH      src/discount.py               3 surviving mutants (boundary `>=` → `>` unnoticed)
  ```

- **Fixed:** what this run fixed, each with the finding it closes. Omit the section in
  report-only mode.
- **Needs a decision:** each finding left for the user, with the options.
- **Unverified:** findings that could not be anchored to quoted code. `None` when empty.
- **Commands run:** each command and its verdict, including checks skipped and why.

## test-audit/v2: YAML with generated Markdown

A `test-audit/v2` report is a copy of `../assets/test-audit.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. The format in code is `test-audit-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `findings.0` is
the first finding.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `test-audit/v2`. `date`: an unquoted date. `commit`: 7 to 40 lowercase hex
  characters. `mode`: `fix` or `report-only`.
- `findings`: `severity` (`CRITICAL`, `HIGH`, `MEDIUM` or `LOW`), `location` (a `path:line` or a
  module, with no spaces) and `finding`, quoting the code. They run worst first, which the model
  checks.
- `fixed`: `fix` and `closes`, in fix mode, and `null` in report-only mode, which leaves the
  section out.
- `needs_decision`: `finding` and `options`. `unverified`: one line per finding.
- `commands`: at least one, each a `command` and its `verdict`.
- An empty list is `[]` and renders as `None`.

**Quote a value that holds `: ` or ` #`, or starts with a quote or a backtick**, because YAML
reads ` #` as a comment and refuses a plain value that starts with a backtick.
