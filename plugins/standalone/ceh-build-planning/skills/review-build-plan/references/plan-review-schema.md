# Plan review schema

The review `review-build-plan` saves to `.agents_workspace/product/plan-reviews/<slug>-<YYYY-MM-DD>.md`. A
new review is a copy of `../assets/plan-review.template.md`, relative to this file. The
`schema: plan-review/v1` line stays as written.

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
