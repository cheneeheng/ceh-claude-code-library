# Session retro schema

The report `diagnose-session` saves: `product/retros/<YYYY-MM-DD>-session-<session-id-prefix>.md`
for in-scope root causes, scrubbed and audited first, and
`.agents_workspace/retros/<YYYY-MM-DD>-session-<session-id-prefix>.md` for out-of-scope root causes,
other findings, and hypotheses. A new file is a copy of `../assets/session-retro.template.md`,
relative to this file. The `schema: session-retro/v1` line stays as written. Secrets in every
quote are masked as `<secret>`.

## Frontmatter

- `session`: the session id diagnosed.
- `date`: the diagnosis date.
- `other_file`: the path of the matching file in the other folder, or `none`. When both files
  exist, each links the other.

## Body

- **Transcript:** the transcript path, plus the number of subagent transcripts read.
- **Symptom:** what went wrong, in one line.
- **Root causes:** one numbered `### <n>. <root cause class>: <one line>` per cause.
  - **First wrong turn:** the `<transcript>:<line>` citation and the quoted line.
  - **Chain:** from the first wrong turn through each step to the visible failure, each with its
    line.
  - **Route:** the skill, or `user: <where the fix lands>`.
  - **Status:** `handed off: <plan, fix record, or commit>` or `open: <why>`.
- **Other findings:** one line each, with the lens and the citation, for findings no symptom
  needed.
- **Hypotheses:** causes believed but not cited, each with what would confirm it.
