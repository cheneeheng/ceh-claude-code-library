# Session retro schema

The report `diagnose-session` saves:
`.agents_workspace/product/retro/<YYYYMMDD-HHMMSS>-<session-id>-session-<diagnosed-id>.yaml`,
with its `.md` rendered beside it, unless the repo's `CLAUDE.md` names another location. A
reference to it names the `.yaml`. One file holds every root cause, whether its fix lands in this
repo or outside it, the other findings and the hypotheses, because the two files of `v1` would
share one name in one folder. Its root causes are scrubbed and audited before it is saved. Its
layout is `../assets/session-retro.template.md`, relative to this file. A new file is written as
`session-retro/v3` YAML, per the section at the end. Secrets in every quote are masked as
`<secret>`.

An older report is still read: a `session-retro/v2` file, a `.md` with no YAML beside it, as
written, and a `session-retro/v1` file, an in-repo file and a local file that link each other
through `other_file`, whose root causes are the root causes of both files.

The copy made for sharing, `<report>-shareable.md`, is not a format of its own: it is the
rendered `.md` with its `generated_from` and `generated_note` keys removed, then scrubbed by hand.

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

## session-retro/v3: YAML with generated Markdown

A `session-retro/v3` report is a copy of `../assets/session-retro.template.yaml`, and the `.md` of
the same name is generated from it in the layout above, beside it. The YAML is the source: agents
read and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml`
and a do-not-edit `generated_note`. The format in code is `session-retro-model.py` beside this
file, and `scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `root_causes.0` is
root cause 1.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `session-retro/v3`. `session`: as in `v2`. `date`: an unquoted date.
- `transcript`: the transcript path. `subagent_transcripts`: how many subagent transcripts were
  read, an integer. `symptom`: one line.
- `root_causes`: `kind` (`Request`, `Guidance`, `Environment`, `Model` or `Claude Code`),
  `cause`, `first_wrong_turn` (a `citation`, `<transcript>:<line>` with no spaces, and its
  `quote`), `chain` (at least two steps, from the first wrong turn to the visible failure, each
  with its line, rendered joined by `→`), `route`, `status` (`handed off` or `open`) and
  `status_detail`, the artifact handed off to or why it is open. The renderer numbers them from 1.
- `other_findings`: `lens`, `finding` and `citation`. `hypotheses`: `cause` and `confirm`.
- An empty list is `[]` and renders as `None`.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment: `route: 'user: ~/.claude/settings.json'`.
