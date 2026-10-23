# QA report schema

The report `explore-app-for-bugs` writes to `.agents_workspace/product/qa/<YYYYMMDD-HHMM>/QA_REPORT.md`,
with screenshots and logs beside it. A new report is a copy of `../assets/qa-report.template.md`,
relative to this file. The `schema: qa-report/v1` line stays as written.

## Frontmatter

- `app`: the app explored.
- `commit`: the commit it ran at.
- `mode`: `report` or `fix`.
- `date`: the run time, from one `date` call.

## Body

- **Launched with:** the documented launch command and the URL or entry point it opened.
- **Mode:** the same mode as the frontmatter.
- **Charters:** one row per charter, `Explore <area> with <technique> to find <risk>`, the actions
  used out of 20, and the IDs of the bugs it found.
- **Bugs:** one `### <ID>: <severity>: <one-line title>` per bug. Severity is `Critical`, `Major`,
  `Minor`, or `Cosmetic`, per the skill's scale.
  - **Status:** `confirmed (reproduced twice)` or `unconfirmed`.
  - **Steps:** numbered, enough to reproduce.
  - **Expected / actual:** what should happen, and what did.
  - **Evidence:** a screenshot path, a console line, or a response body.
  - **Fix:** fix mode only: the commit and the re-run result. Omit in report mode.
- **Usability notes (not bugs):** confusing wording, layout, or flow, kept apart from the bugs.
- **Not explored:** the flows, roles, or environments no charter covered, and why.
