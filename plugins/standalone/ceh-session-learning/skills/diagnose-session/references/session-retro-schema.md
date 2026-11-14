# Session retro schema

The report `diagnose-session` saves:
`.agents_workspace/product/retros/<YYYYMMDD-HHMMSS>-<session-id>-session-<diagnosed-id>.md`,
unless the repo's `CLAUDE.md` names another location. One file holds every root cause, whether its
fix lands in this repo or outside it, the other findings and the hypotheses, because the two files
of `v1` would share one name in one folder. Its root causes are scrubbed and audited before it is
saved. A new file is a copy of `../assets/session-retro.template.md`, relative to this file. The
`schema: session-retro/v2` line stays as written. Secrets in every quote are masked as `<secret>`.

A `session-retro/v1` file, an in-repo file and a local file that link each other through
`other_file`, is still read: its root causes are the root causes of both files.

## Frontmatter

- `session`: the session id diagnosed.
- `date`: the diagnosis date.

## Body

- **Transcript:** the transcript path, plus the number of subagent transcripts read.
- **Symptom:** what went wrong, in one line.
- **Root causes:** one numbered `### <n>. <root cause class>: <one line>` per cause.
  - **First wrong turn:** the `<transcript>:<line>` citation and the quoted line.
  - **Chain:** from the first wrong turn through each step to the visible failure, each with its
    line.
  - **Route:** the skill, or `user: <where the fix lands>` for a fix outside this repo.
  - **Status:** `handed off: <plan, fix record, or commit>` or `open: <why>`.
- **Other findings:** one line each, with the lens and the citation, for findings no symptom
  needed.
- **Hypotheses:** causes believed but not cited, each with what would confirm it.
