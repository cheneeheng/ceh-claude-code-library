# First-run audit schema

The report `simulate-newcomer-first-run` writes to
`.agents_workspace/product/ux-audits/<target>/run-<NNN>/UX_AUDIT.md`, with a zero-padded run index so a
re-run never overwrites a prior run's evidence, and the raw walker transcripts beside it. A new
report is a copy of `../assets/first-run-audit.template.md`, relative to this file. The
`schema: first-run-audit/v1` line stays as written.

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
