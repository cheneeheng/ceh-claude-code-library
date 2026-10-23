# Interface audit schema

The report `audit-interface` writes to `.agents_workspace/product/ux-audits/<target>/run-<NNN>/UX_AUDIT.md`,
with a zero-padded run index so a re-run never overwrites prior evidence, and the walker transcripts
and screenshots beside it. A new report is a copy of `../assets/interface-audit.template.md`,
relative to this file. The `schema: interface-audit/v1` line stays as written.

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
