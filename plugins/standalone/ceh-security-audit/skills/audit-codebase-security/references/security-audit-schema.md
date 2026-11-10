# Security audit schema

The report `audit-codebase-security` saves to
`.agents_workspace/product/security-audit/SECURITY_AUDIT-<YYYY-MM-DD>.md`, never a committed path. Its
layout is `../assets/security-audit.template.md`, relative to this file. A new report is written
as `security-audit/v2` YAML, per the section at the end, and an older `security-audit/v1` report
stays as written, its `schema:` line included.

## Frontmatter

- `repo`: the repo audited.
- `commit`: the short commit audited.
- `date`: the audit date.

## Sections

- **Attack surface:** the entry points, trust boundaries, assets, and attackers from step 1.
- **Findings:** one numbered row per finding. Severity is `critical`, `high`, `medium`, or `low`.
  Confidence is `confirmed` (traced end to end, or proven by a local test) or `likely`. Category is the class of hole. Attacker names who can reach it, because severity follows
  reachability. Location is a `path:line`. Attack says what the attacker does, and Fix the change
  that closes it. A row reads like
  `| 1 | high | confirmed | Access control | signed-in | app/api/orders.py:52 | GET /orders/{id} returns any user's order | Filter by owner_id == current_user.id |`.
- **Possible:** leads that could not be traced end to end, each with what would settle it.
- **Not checked:** each category or check not run, with the reason and the command that would run
  it.

## security-audit/v2: YAML with generated Markdown

A `security-audit/v2` report is `SECURITY_AUDIT-<YYYY-MM-DD>.yaml`, a copy of
`../assets/security-audit.template.yaml`, and the `.md` of the same name is generated from it in
the `v1` layout above, beside it. The YAML is the source: agents read and edit it, and nobody
edits the Markdown, which opens with `generated_from: SECURITY_AUDIT-<YYYY-MM-DD>.yaml` and a
do-not-edit `generated_note`. The format in code is `security-audit-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/SECURITY_AUDIT-<date>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/SECURITY_AUDIT-<date>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `findings.0` is
finding 1.

**Keys**, each required, and no other key allowed:

- `schema`: `security-audit/v2`. `repo`: as in `v1`. `commit`: 7 to 40 lowercase hex characters,
  never a name such as `HEAD`, because `write-evidence-report` runs `git log <commit>..HEAD` on it.
  `date`: an unquoted date.
- `attack_surface`: the Attack surface section's text, in a `|` block.
- `findings`: `severity` (`critical`, `high`, `medium` or `low`), `confidence` (`confirmed` or
  `likely`), `category`, `attacker`, `location` (a `path:line` with no spaces), `attack` and `fix`,
  each one line. The renderer numbers the findings from 1, so no number is stored.
- `possible`: `lead` and `settle`, what would settle it. `not_checked`: `check`, `reason` and
  `command`. An empty list is `[]` and renders as `None`.

**Free text goes in `|` blocks or quotes**, because ` #` starts a YAML comment, and every value is
strict, so quote a value such as `1.10` that must stay text.
