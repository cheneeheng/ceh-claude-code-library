# Evidence schema

The committed `product/EVIDENCE.md` that `write-evidence-report` keeps. A new file is a copy of
`../assets/evidence.template.md`, relative to this file. The `schema: evidence/v1` line stays as
written. A file without it gets the template's frontmatter on the next run, and its sections stay
as they are.

## Frontmatter

- `product`: the product the evidence is for.

## Run sections

Each run adds one `## YYYY-MM-DD at <short-sha>` section below the title, newest first. Earlier
sections are never edited: each one is what was proven at its commit, and a plan's Record cites it
by date.

- **Tree:** `clean`, or `dirty (<n> files)`.
- **Area table:** one row per area, in the template's order.
  - **Status:** Tests is `passed`, `failed`, or `not run`. The other areas are `passed`,
    `open issues`, `stale (<n>)` (the report is `<n>` commits behind), or `not run`.
  - **Result:** the figure copied from the area's report or this session's test run, never
    estimated: the test command and its summary line, the QA bugs found and fixed, the metric and
    its value on its machine, the security counts by severity, the usability blocker and friction
    counts, or the plan items built and missing.
  - **Checked at:** the SHA, or the date when the report gives no SHA.
- **Open issues:** one bullet per issue, with its area and its severity where the report gives
  one: critical and high security findings, confirmed QA bugs not yet fixed, usability blockers,
  and plan items missing or failing their check. `None` when empty.
- **Claims:** one sentence each that a launch post may state, with its area and figure.
- **Not run:** each area not run, with the reason and the skill that produces it.
