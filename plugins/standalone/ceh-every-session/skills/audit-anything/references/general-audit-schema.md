# General audit schema

The audit `audit-anything` saves to
`.agents_workspace/product/audit/general/<YYYYMMDD-HHMMSS>-<session-id>-<target>.yaml`, with its
`.md` rendered beside it. Every run writes a new file, never edited after: a later audit of the
same subject is a new file, and a fix goes in a fix record or a plan. A reference to it names the
`.yaml`. Its layout is `../assets/general-audit.template.md`, relative to this file. The time comes
from one `date +%Y%m%d-%H%M%S` call, and the session id is the whole id of the session that ran
the audit. `<target>` names the subject, by the first of these that applies:

- A kebab-case name the user gives.
- One file or folder: its path relative to the repo root, or to the working directory outside a
  repository, with every `/` and `.` replaced by `-`, so `docs/STRATEGY.md` is
  `docs-STRATEGY-md`. The repo root itself is the repo folder's name.
- Several paths: their common folder, named the same way, when they share one below the root,
  otherwise the first path followed by `-and-<n>-more`.

## Body

- **Subject** and **Criteria:** the paths audited, and what they were judged against.
- **Summary:** what the audit found, in a few lines.
- **Findings:** one bullet per finding, worst first: the severity `HIGH`, `MEDIUM` or `LOW`, the
  location, and the finding.
- **Not covered:** each part of the subject or criterion the audit did not judge, and why.

## general-audit/v1: YAML with generated Markdown

A `general-audit/v1` audit is a copy of `../assets/general-audit.template.yaml`, and the `.md` of
the same name is generated from it in the layout above, beside it. The YAML is the source, and
nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a do-not-edit
`generated_note`. The format in code is `general-audit-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `findings.0` is the
first finding.

**Keys**, all required, and no other key allowed:

- `schema`: `general-audit/v1`. `date`: an unquoted date. `target`: as in the file name.
- `subject`: a list of the paths audited, at least one. `criteria`: a list of what the subject was
  judged against, at least one: file paths or stated sentences.
- `summary`: a `|` block, what the audit found in a few lines.
- `findings`: each with `severity` (`HIGH`, `MEDIUM` or `LOW`), `location` (a path, optionally
  followed by `:<line>`, with no spaces, and for something missing the file or folder it belongs
  in) and `finding` (one line). Ordered worst first, which the model checks. An empty list is `[]`
  and renders as `None`.
- `not_covered`: a list of each part of the subject or criterion the audit did not judge, with
  why, `[]` when none.

The format has no rounds, no status and no resolution, because the file is never edited. The
`independent-reader` agent's `<location> | <label> | <comment>` line maps to `location`,
`severity` and `finding`, and its `## Not covered` to `not_covered`.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote or a backtick**, because
YAML reads ` #` as a comment and refuses a plain value that starts with a backtick.
