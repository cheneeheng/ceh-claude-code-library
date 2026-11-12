# Glossary schema

The committed glossary that `maintain-glossary` keeps. A new glossary is a `glossary/v2` YAML (see
the last section), and its `GLOSSARY.md` is rendered in the `v1` layout of
`../assets/glossary.template.md`, relative to this file, described below. A `v1` file's
`schema: glossary/v1` line stays as written.

## Entries

- One entry per concept, in alphabetical order by term.
- **Term:** bold, then `—` and one or two sentences: what it is, in domain words.
- **Avoid:** every other word for the same concept. Omit when there is none.
- **Not to be confused with:** a nearby term with a different meaning, in bold. Omit when there is
  none.

## glossary/v2: YAML with generated Markdown

A `glossary/v2` glossary is `GLOSSARY.yaml` at the repo root, or `docs/GLOSSARY.yaml` when the
repo keeps its docs there, a copy of `../assets/glossary.template.yaml`, and `GLOSSARY.md` beside
it is generated from it in the `v1` layout above. The YAML is the source: agents read and edit it,
and nobody edits the Markdown, which opens with `generated_from: GLOSSARY.yaml` and a do-not-edit
`generated_note`. A `v1` `GLOSSARY.md` with no `GLOSSARY.yaml` beside it is still read as `v1`,
and converted before anything amends it. The format in code is `glossary-model.py` beside this
file, and `scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check GLOSSARY.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render GLOSSARY.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `glossary/v2`.
- `entries`: a list, each `term` (one line, the chosen word), `definition` (a `|` block, Markdown,
  in domain words), `avoid` (a list of one-line aliases, `[]` when none) and `not_confused_with`
  (a list of one-line nearby terms, `[]` when none). A nearby term need not have its own entry.
- `open`: a list of terms not yet settled, each `term` and `question` (a `|` block), `[]` when
  none. It may name a settled term whose definition is disputed. Rendered as `## Open terms`.
- `notes` (optional): a `|` block of Markdown, rendered as `## Notes`, for paragraphs a `v1` file
  held outside its entries.

**Rules.** `entries` and `open` are not both empty. Terms are unique across `entries`, ignoring
case and surrounding whitespace, and an entry's `avoid` neither repeats its own term nor lists an
alias twice under the same comparison. Write entries in any order: the renderer sorts them by
term, ignoring case, and never rewrites a definition. Empty `avoid` and `not_confused_with` lines
are left out. Terms and aliases render as literal text, with Markdown delimiters escaped.

**Converting a `v1` file.** Before amending a `GLOSSARY.md` that has no YAML, first copy it
outside the repository, to the session's scratch or temp directory: the render hook writes the new
Markdown over it as soon as the YAML is saved. Then carry every entry into `entries` word for word,
every paragraph outside an entry into `notes`, and every term still unresolved into `open`, and
compare the rendered Markdown with the copy. When any entry or paragraph of the copy is missing,
restore the copy, delete the YAML, and report what was lost.

**Quoting:** single-quote any value that starts with `*`, `{`, `[` or `` ` ``, contains `: ` or
` #`, or holds a backslash, such as `'C:\tools'`. Aliases and nearby terms are block lists in the
template, which needs none of that inside a flow list. Definitions, questions and notes are `|`
blocks.
