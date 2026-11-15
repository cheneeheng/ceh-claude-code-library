# Investor outreach schema

The outreach notes `write-investor-materials` saves to
`.agents_workspace/product/business/INVESTOR_OUTREACH.yaml`, beside the deck, with its `.md`
rendered beside it, local and not committed. A reference to it names the `.yaml`. Its layout is
`../assets/investor-outreach.template.md`, relative to this file. A new file is written as
`investor-outreach/v2` YAML, per the section at the end. A file saved as `investor-outreach/v1`,
an `INVESTOR_OUTREACH.md` with no YAML beside it, is still edited in place when the skill next
updates it, its `schema:` line included.

## Frontmatter

- `plan`: the path to the business plan the notes are built from.

## Body

- **Fit:** the investor profile this plan matches: stage, cheque size, sector, and the thesis.
- **Investors:** the names the user supplied, or `none supplied`. The skill never invents names.
- **Email:** at most 120 words. The subject is the one-liner. The body says what it is, the
  traction number, the ask, and the link.
- **Follow-up:** one line, sent two weeks later, with something new since the first email.
- Notes written on an unvalidated plan carry `Draft: gate <N>/8` as their first body line.

## investor-outreach/v2: YAML with generated Markdown

An `investor-outreach/v2` file is `INVESTOR_OUTREACH.yaml`, a copy of
`../assets/investor-outreach.template.yaml`, and `INVESTOR_OUTREACH.md` is generated from it in
the layout above, beside it. The YAML is the source: agents read and edit it, and nobody edits the
Markdown, which opens with `generated_from: INVESTOR_OUTREACH.yaml` and a do-not-edit
`generated_note`. The email body sits unchanged between the prettier-ignore markers, so copy it
from there. The format in code is `investor-outreach-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/INVESTOR_OUTREACH.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/INVESTOR_OUTREACH.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required, and no other key allowed:

- `schema`: `investor-outreach/v2`. `plan`: as in `v1`.
- `pmf_gate`: the plan's gate, an integer from 0 to 8, and `draft`: `true` on an unvalidated plan,
  which renders the `Draft: gate <N>/8` line. A `pmf_gate` below 8 needs `true`.
- `fit`: `stage`, `cheque`, `sector` and `thesis`, each one line.
- `investors`: the names the user supplied, and `[]` when none, which renders as `none supplied`.
- `email`: `subject`, one line, and `body`, a `|` block of at most 120 words.
- `follow_up`: one line.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote**, because YAML reads
` #` as a comment.
