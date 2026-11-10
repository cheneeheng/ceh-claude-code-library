# First-run audit schema

The report `simulate-newcomer-first-run` writes to
`.agents_workspace/product/ux-audits/<target>/run-<NNN>/UX_AUDIT.md`, with a zero-padded run index so a
re-run never overwrites a prior run's evidence, and the raw walker transcripts beside it. Its
layout is `../assets/first-run-audit.template.md`, relative to this file. A new report is written
as `first-run-audit/v2` YAML, per the section at the end, and an older `first-run-audit/v1` report
stays as written, its `schema:` line included.

## Frontmatter

- `target`: the product walked.
- `run`: the zero-padded run index, matching the folder.
- `date`: the run date.
- `gate`: the gate score out of 5, or out of the remainder with N/A criteria (`4/4, 1 N/A`).

## Header

- **Goal:** the one sentence from step 1.
- **Milestones & budget:** each milestone with its action budget.
- **Audience baseline:** verbatim from step 2.
- **Frozen set:** verbatim: what a newcomer actually receives.
- **Walkers:** the personas run, those skipped and why, and how they ran: `in parallel`,
  `serially`, or `in isolated copies`.
- **Method:** stays as the template words it.
- **Gate:** the same score as the frontmatter.

## Sections

- **Results:** one row per persona: the furthest milestone reached, why the walk stopped, actions
  used against the budget, external lookups, machine wait in seconds, and the ID of its first
  stall. Then the estimated newcomer time to goal, from the cost model, not measured, plus the
  machine wait.
- **Findings:** one `### <ID> — <severity> — <one-line title>` per finding. Severity is `Blocker`,
  `Detour`, `Friction`, or `Polish`. **Where** is the `file:line`, screen, or command. **Persona**
  is who stalled. **Expected / got** is what they thought would happen, and what happened.
  **Missing knowledge** is the fact they needed and did not have. **Fix** is the concrete change.
- **Hypotheses:** suspected problems no walker stalled on, unranked.
- **Not covered:** what this method cannot measure, and what was delegated to accessibility.

## first-run-audit/v2: YAML with generated Markdown

A `first-run-audit/v2` report is `UX_AUDIT.yaml`, a copy of `../assets/first-run-audit.template.yaml`,
and `UX_AUDIT.md` is generated from it in the `v1` layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: UX_AUDIT.yaml` and a do-not-edit `generated_note`. The format in code is
`first-run-audit-model.py` beside this file, and `scripts/artifact.py` in the skill checks and
renders it through uv, picking the model by the file's `schema:` key, since the interface audit
saves a `UX_AUDIT.yaml` too:

```bash
uv run --script scripts/artifact.py check <dir>/UX_AUDIT.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/UX_AUDIT.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `results.0` is the
first persona's row.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `first-run-audit/v2`. `target`: as in `v1`. `run`: an int, rendered zero-padded to
  three digits (`007`) to match the `run-<NNN>` folder. `date`: an unquoted date.
- `commit`: the target's commit as walked, 7 to 40 lowercase hex characters, never a name such as
  `HEAD`, because `write-evidence-report` runs `git log <commit>..HEAD` on it.
- `goal`: one line. `milestones`: `name` and `budget` (actions), at least one. `audience` and
  `frozen_set`: verbatim, in `|` blocks.
- `walkers`: `run` (the personas run, at least one), `skipped` (`persona` and `why`) and `mode`
  (`in parallel`, `serially` or `in isolated copies`).
- `gate`: `score`, `out_of` and `na`, with `score <= out_of` and `out_of + na == 5`, rendered
  `<score>/5` when `na` is 0 and `<score>/<out_of>, <na> N/A` otherwise.
- `results`: `persona`, `furthest`, `stop_reason`, `actions`, `budget` (the budget of the milestone
  it was walking, rendered `<actions>/<budget>`), `lookups`, `wait_s` (seconds) and `first_stall`
  (optional), which names a finding in the file.
- `minutes`: the estimated newcomer time to goal from the cost model. The renderer adds the machine
  wait, the sum of every `wait_s`.
- `findings`: `id` (unique), `severity` (`Blocker`, `Detour`, `Friction` or `Polish`), `title`,
  `where`, `persona`, `expected`, `got`, `missing_knowledge` and `fix`.
- `hypotheses` and `not_covered`: one string each. An empty list is `[]` and renders as `None`.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.
