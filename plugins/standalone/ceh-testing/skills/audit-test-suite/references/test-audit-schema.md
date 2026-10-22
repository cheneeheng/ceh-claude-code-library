# Test audit schema

The report `audit-test-suite` saves to `.agents_workspace/test-audits/<YYYY-MM-DD>.md`. A subagent
in report-only mode returns it instead, and its caller saves it. A new report is a copy of
`../assets/test-audit.template.md`, relative to this file. The `schema: test-audit/v1` line stays
as written.

## Frontmatter

- `date`: the audit date.
- `commit`: the short SHA audited.
- `mode`: `fix` or `report-only`.

## Sections

- **Findings:** worst first, one line each: the severity, the `path:line` (or the module, for a
  mutation result), and the finding, quoting the code it is about. For example:

  ```
  CRITICAL  tests/unit/test_billing.py:41  no assertion — only checks no exception raised
  HIGH      src/discount.py               3 surviving mutants (boundary `>=` → `>` unnoticed)
  ```

- **Fixed:** what this run fixed, each with the finding it closes. Omit the section in
  report-only mode.
- **Needs a decision:** each finding left for the user, with the options.
- **Unverified:** findings that could not be anchored to quoted code. `None` when empty.
- **Commands run:** each command and its verdict, including checks skipped and why.
