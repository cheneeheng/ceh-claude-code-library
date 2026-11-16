# Plan review schema

The review `review-build-plan` saves to
`.agents_workspace/product/review/plan/<YYYYMMDD-HHMMSS>-<session-id>-<slug>.yaml`, with its
`.md` rendered beside it. A reference to it names the `.yaml`. Its layout is
`../assets/plan-review.template.md`, relative to this file. A new review is written as
`plan-review/v2` YAML, per the section at the end, and an older `plan-review/v1` review, a `.md`
with no YAML beside it, stays as written, its `schema:` line included.

## Frontmatter

- `plan`: the path of the plan reviewed.
- `date`: the review date.
- `verdict`: `Ready to build`, `Revise first`, or `Rethink`, per the verdict table in the skill.

## Body

- **Verdict:** the same verdict as the frontmatter.
- **Lenses:** the lenses run, for example `Scope, Engineering, Design`, then each lens skipped
  with its reason, for example `Skipped developer experience: no developer callers.`
- **Findings table:** one row per finding, numbered from 1. Severity is `blocking` or `advisory`.
  Plan line is the plan line quoted. Finding says what is wrong, and Fix is the edit. A row reads
  like
  `| 1 | Engineering | blocking | Phase 3 Check: "the app runs" | Proves nothing about the import it builds | uv run pytest tests/test_import.py passes |`.
- **Questions for the owner:** each question only the plan's owner can answer, with a recommended
  answer. `None` when empty.
- **Unverified:** findings not checked against the code or the repo, each with why. `None` when
  empty.
- **Fixes made:** fix mode only: what was edited and what was left open. Omit the section outside
  fix mode.

## plan-review/v2: YAML with generated Markdown

A `plan-review/v2` review is `<YYYYMMDD-HHMMSS>-<session-id>-<slug>.yaml`, a copy of
`../assets/plan-review.template.yaml`, and the `.md` of the same name is generated from it in the
layout above, beside it. The YAML is the source: agents read and edit it, and nobody edits the
Markdown, which opens with `generated_from: <file>.yaml` and a do-not-edit `generated_note`. The
format in code is `plan-review-model.py` beside this file, and `scripts/artifact.py` in the skill
checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `findings.0` is
finding 1.

**Keys**, each required, and no other key allowed:

- `schema`: `plan-review/v2`. `plan`, `verdict`: as in `v1`. `date`: an unquoted date.
- `lenses`: the lenses run, at least one. `skipped`: `lens` and `reason` per lens skipped.
- `findings`: `lens`, `severity` (`blocking` or `advisory`), `plan_line`, `finding` and `fix`,
  each one line. The renderer numbers them from 1, so no number is stored. `Ready to build` allows
  no blocking finding, and `Revise first` needs one.
- `questions`: `question` and `recommended`. `unverified`: `finding` and `why`.
- `fixes_made`: one line per edit made or left open, in fix mode, and `null` outside it, which
  leaves the section out.
- An empty list is `[]` and renders as `None`, or `No findings.` for `findings`.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment, so a quoted plan line is written `plan_line: 'Phase 3 Check: "the app runs"'`.
Every value is strict, so quote a value such as `1.10` that must stay text.
