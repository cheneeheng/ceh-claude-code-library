# Interface audit schema

The report `audit-interface` writes to
`.agents_workspace/product/ux-audits/<target>/run-<NNN>/UX_AUDIT.yaml`, with its `.md` rendered
beside it, a zero-padded run index so a re-run never overwrites prior evidence, and the walker
transcripts and screenshots beside it. A reference to it names the `.yaml`. Its layout is `../assets/interface-audit.template.md`, relative to this
file. A new report is written as `interface-audit/v2` YAML, per the section at the end, and an
older `interface-audit/v1` report stays as written, its `schema:` line included.

## Frontmatter

- `target`: the product audited.
- `surface`: the UI, CLI, or API surface walked.
- `run`: the zero-padded run index, matching the folder.
- `date`: the run date.
- `gate`: the gate score out of 5, or out of the remainder with N/A criteria (`4/4, 1 N/A`).

## Header

- **Goal(s) walked:** the concrete in-product tasks, each with its action budget.
- **Audience baseline:** verbatim: what the intended audience already knows.
- **Allowlist:** what the walkers were permitted to read.
- **Walkers:** the personas run, then those skipped and why.
- **Method:** stays as the template words it.
- **Gate:** the same score as the frontmatter.

## Sections

- **Five questions:** one row per screen or command, answering the five questions from the walks.
- **Findings:** one `### <ID> — <severity> — <title>` per finding. Severity is `Blocker`, `Detour`,
  `Friction`, or `Polish`. **Where** is the screen, command, or `file:line`. **Persona** is who
  stalled. **Expected / got** is what they thought would happen, and what happened. **Fix** is the
  concrete change.
- **Hypotheses:** suspected problems no walker stalled on, unranked.
- **Delegated:** what went to `make-ui-accessible`, `design-ui`, or `audit-error-messages`.
- **Not covered:** what this run did not walk or cannot measure.

## interface-audit/v2: YAML with generated Markdown

An `interface-audit/v2` report is `UX_AUDIT.yaml`, a copy of `../assets/interface-audit.template.yaml`,
and `UX_AUDIT.md` is generated from it in the `v1` layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: UX_AUDIT.yaml` and a do-not-edit `generated_note`. The format in code is
`interface-audit-model.py` beside this file, and `scripts/artifact.py` in the skill checks and
renders it through uv, picking the model by the file's `schema:` key, since the first-run audit
saves a `UX_AUDIT.yaml` too:

```bash
uv run --script scripts/artifact.py check <dir>/UX_AUDIT.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/UX_AUDIT.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `findings.0` is the
first finding.

**Keys**, each required, and no other key allowed:

- `schema`: `interface-audit/v2`. `target` and `surface`: as in `v1`. `run`: an int, rendered
  zero-padded to three digits (`007`) to match the `run-<NNN>` folder. `date`: an unquoted date.
- `commit`: the target's commit as walked, 7 to 40 lowercase hex characters, never a name such as
  `HEAD`, because `write-evidence-report` runs `git log <commit>..HEAD` on it.
- `goals`: `goal` and `budget` (actions), at least one. `audience` and `allowlist`: verbatim, in
  `|` blocks.
- `walkers`: `run` (the personas run, at least one) and `skipped` (`persona` and `why`).
- `gate`: `score`, `out_of` and `na`, with `score <= out_of` and `out_of + na == 5`, rendered
  `<score>/5` when `na` is 0 and `<score>/<out_of>, <na> N/A` otherwise.
- `five_questions`: `screen`, `where_am_i`, `what_for`, `primary_action`, `what_happened` and
  `way_out`, one line each.
- `findings`: `id` (unique), `severity` (`Blocker`, `Detour`, `Friction` or `Polish`), `title`,
  `where`, `persona`, `expected`, `got` and `fix`.
- `hypotheses` and `not_covered`: one string each. `delegated`: `skill` and `what`. An empty list
  is `[]` and renders as `None`.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.
